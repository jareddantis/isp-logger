from flask import Flask, render_template
from json import dumps
from sqlite3 import connect
from time import time


# Create Flask instance
app = Flask(__name__, template_folder='templates')


@app.route('/')
def dashboard_page():
    return render_template('dashboard.html')


@app.route('/api/v1/isp', methods=['GET'])
def get_isp_info():
    autonomous_systems = {}
    isp_history = []
    first_seen = 0
    last_seen = 0
    last_asn = None
    last_as_name = None

    # Open connection to SQLite database
    con = connect('isp.db')
    cur = con.cursor()

    # Iterate through all rows
    cur.execute('SELECT * FROM isp_history ORDER BY timestamp DESC')
    now = time() * 1000
    for row in cur:
        timestamp, asn, as_name, ip, loc = row

        # If timestamp is more than 12 hours ago, abort
        if (now - timestamp) > 43200000:
            break
        
        # Add to list of ASes
        if asn not in autonomous_systems.keys():
            autonomous_systems[asn] = as_name

        # If this ASN is different, add it to the list
        first_seen = timestamp
        if asn != last_asn:
            if last_asn != None:
                # This is not the first row in the database, add the last AS to the list.
                isp_history.append({
                    'asn': last_asn,
                    'as_name': last_as_name,
                    'first_seen': first_seen,
                    'last_seen': last_seen,
                    'ip': ip,
                    'location': loc
                })

            # Update current ASN
            last_asn = asn
            last_as_name = as_name
            last_seen = timestamp
    else:
        # If we got to this point, the ISP did not change enough times to be added
        # as a row in the history. Add it now before we finish.
        isp_history.append({
            'asn': last_asn,
            'as_name': last_as_name,
            'first_seen': first_seen,
            'last_seen': last_seen,
            'ip': ip,
            'location': loc
        })

    # Close connection
    cur.close()

    # Return the list of ISPs
    return dumps({
        'autonomous_systems': autonomous_systems,
        'history': isp_history
    })


if __name__ == '__main__':
    app.run()
