import requests
from sqlite3 import connect
import time


def get_isp():
    # Get current time
    now = int(time.time() * 1000)

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

    return now, as_number, as_name


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
            (timestamp INTEGER PRIMARY KEY NOT NULL,
             asn       TEXT                NOT NULL,
             as_name   TEXT                NOT NULL)''')

        # Insert data into database
        now, as_number, as_name = get_isp()
        cur.execute("INSERT INTO isp_history VALUES ({0}, '{1}', '{2}')".format(now, as_number, as_name))

        # Close connection
        cur.close()
        con.commit()
