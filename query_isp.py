from requests import get
from sqlite3 import connect
from time import time


if __name__ == '__main__':
    try:
        # Connect to SQLite database
        con = connect('isp.db')
        cur = con.cursor()
    except Exception as e:
        print(e)
        exit(1)
    else:
        # Create table if it doesn't exist yet
        cur.execute('''CREATE TABLE IF NOT EXISTS isp_history
            (start     INTEGER PRIMARY KEY NOT NULL,
             end       INTEGER             NOT NULL,
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
            as_name = 'Unknown'
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
        if last_record is None:
            # No existing records, insert new record
            cur.execute("INSERT INTO isp_history VALUES ({0}, {1}, '{2}', '{3}', '{4}', '{5}')".format(now, now, as_number, as_name, ip_addr, location))
        else:
            # Update existing record's end column
            cur.execute("UPDATE isp_history SET end={0} WHERE start={1}".format(now, last_record[0]))

        # Close connection
        cur.close()
        con.commit()
