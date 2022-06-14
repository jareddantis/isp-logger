import json
import requests
from sqlite3 import connect, Cursor
import time


def get_isp(cur: Cursor):
    # Get current time
    now = int(time.time())

    # Get AS info from ipinfo.io
    ipinfo_url = 'https://ipinfo.io/json'
    try:
        ipinfo_response = requests.get(ipinfo_url, timeout=5)
        ipinfo_json = ipinfo_response.json()
    except:
        as_number = '-1'
        as_name = 'No data'
    else:
        # Split AS info into ASN and AS name
        as_info: str = ipinfo_json['org']
        as_split = as_info.split(' ', 1)
        as_number = as_split[0]
        as_name = as_split[1]

    # Insert data into database
    cur.execute("INSERT INTO isp_history VALUES (NULL, '{0}', '{1}', {2})".format(as_number, as_name, now))


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
            (id        INTEGER PRIMARY KEY,
             asn       TEXT                NOT NULL,
             as_name   TEXT                NOT NULL,
             timestamp INTEGER             NOT NULL)
        ''')

        get_isp(cur)
        cur.close()
        con.commit()