from requests import get
from sqlite3 import connect, Connection
from time import sleep, time
import schedule
import signal


class GracefulKiller:
    """
    https://stackoverflow.com/a/31464349
    """
    def __init__(self, con: Connection):
        self._kill_now = False
        self._con = con
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)
    
    @property
    def kill_now(self) -> bool:
        return self._kill_now

    def exit_gracefully(self, *args):
        self._kill_now = True
        self._con.close()


def get_isp(con: Connection):
    # Create table if it doesn't exist yet
    cur = con.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS isp_history
        (start     INTEGER PRIMARY KEY NOT NULL,
            `end`     INTEGER             NOT NULL,
            asn       INTEGER             NOT NULL,
            as_name   TEXT                NOT NULL,
            ip        TEXT                NOT NULL,
            location  TEXT                NOT NULL)''')

    # Get AS info from ipinfo.io
    now = int(time() * 1000)
    try:
        ipinfo_response = get('https://ipinfo.io/json', timeout=5)
        ipinfo_json = ipinfo_response.json()
    except:
        as_number = -1
        as_name = 'No connection'
        ip_addr = '-'
        location = '-'
    else:
        # Get ASN and AS name
        as_info: str = ipinfo_json['org']
        as_split = as_info.split(' ', 1)
        as_number = as_split[0][2:]
        as_name = as_split[1]

        # Get IP
        ip_addr = ipinfo_json['ip']

        # Construct location string
        location = '{0}, {1}, {2}'.format(ipinfo_json['city'], ipinfo_json['region'], ipinfo_json['country'])

    # Try to get most recent record
    cur.execute('SELECT * FROM isp_history WHERE start=(SELECT max(start) FROM isp_history)')
    last_record = cur.fetchone()

    # Is there an existing record in the database?
    if last_record is None or now - last_record[1] > 150000:
        if last_record is not None:
            # Last record is more than 1 minute ago, so we should signify that there was a gap in data.
            cur.execute("INSERT INTO isp_history VALUES ({0}, {1}, {2}, '{3}', '{4}', '{5}')".format(last_record[1] + 1, now - 1, -1, 'No connection', '-', '-'))

        # Insert new record
        cur.execute("INSERT INTO isp_history VALUES ({0}, {1}, {2}, '{3}', '{4}', '{5}')".format(now, now, as_number, as_name, ip_addr, location))
    else:
        # Update existing record's end column
        cur.execute("UPDATE isp_history SET `end`={0}, ip='{1}' WHERE start={2}".format(now, ip_addr, last_record[0]))

    # Commit changes
    con.commit()


if __name__ == '__main__':
    # Connect to database
    con = connect('isp.db')
    int_handler = GracefulKiller(con)

    # Run at the start of every system clock minute
    try:
        schedule.every(2).minute.at(':00').do(get_isp, con)
        while not int_handler.kill_now:
            schedule.run_pending()
            sleep(0.1)
    except KeyboardInterrupt:
        int_handler.exit_gracefully()
        exit()
