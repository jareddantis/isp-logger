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
            (timestamp INTEGER PRIMARY KEY NOT NULL,
             asn       INTEGER             NOT NULL,
             as_name   TEXT                NOT NULL)''')

        # Get AS info from ipinfo.io
        now = int(time() * 1000)
        try:
            ipinfo_response = get('https://ipinfo.io/json', timeout=5)
            ipinfo_json = ipinfo_response.json()
        except:
            as_number = -1
            as_name = 'Unknown'
        else:
            # Split AS info into ASN and AS name
            as_info: str = ipinfo_json['org']
            as_split = as_info.split(' ', 1)
            as_number = as_split[0][2:]
            as_name = as_split[1]

        # Insert data into database
        cur.execute("INSERT INTO isp_history VALUES ({0}, '{1}', '{2}')".format(now, as_number, as_name))

        # Close connection
        cur.close()
        con.commit()
