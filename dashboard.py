from flask import Flask, render_template, request
from json import dumps
from requests import get
from sqlite3 import connect


# Create Flask instance
app = Flask(__name__, template_folder='templates')


@app.route('/')
def dashboard_page():
    return render_template('dashboard.html')


@app.route('/api/v1/isp', methods=['GET'])
def get_isp_info():
    isp_history = []
    first_seen = 0
    last_seen = 0
    last_asn = None
    last_as_name = None

    # Get AS info from ipinfo.io
    try:
        ipinfo_response = get('https://ipinfo.io/json', timeout=5)
        ipinfo_json = ipinfo_response.json()
    except:
        current_isp = {
            'ip': '0.0.0.0',
            'hostname': 'No data',
            'location': 'No data',
            'org': 'No data'
        }
    else:
        # Split AS info into ASN and AS name
        current_isp = {
            'ip': ipinfo_json['ip'],
            'hostname': ipinfo_json['hostname'],
            'location': "{0}, {1}, {2} {3}".format(ipinfo_json['city'], ipinfo_json['region'], ipinfo_json['country'], ipinfo_json['postal']),
            'org': ipinfo_json['org']
        }

    # Get number of history entries to return
    num_entries = request.args.get('num_entries', type=int, default=10)

    # Open connection to SQLite database
    con = connect('isp.db')
    cur = con.cursor()

    # Iterate through all rows
    cur.execute('SELECT * FROM isp_history ORDER BY timestamp DESC')
    for row in cur:
        timestamp, asn, as_name = row

        # If this ASN is different, add it to the list
        if asn != last_asn:
            if last_asn != None:
                # This is not the first row in the database, add the last AS to the list.
                isp_history.append({
                    'asn': last_asn,
                    'as_name': last_as_name,
                    'first_seen': first_seen,
                    'last_seen': last_seen
                })

                # If the ISP history is now <num_entries> items long, abort
                if len(isp_history) == num_entries:
                    break

            # Update current ASN
            last_asn = asn
            last_as_name = as_name
            last_seen = timestamp
        else:
            # This is the same ISN, update the first seen timestamp
            first_seen = timestamp
    else:
        # If we got to this point, the ISP did not change enough times to be added
        # as a row in the history. Add it now before we finish.
        isp_history.append({
            'asn': last_asn,
            'as_name': last_as_name,
            'first_seen': first_seen,
            'last_seen': last_seen
        })

    # Close connection
    cur.close()

    # Return the list of ISPs
    return dumps({
        'now': current_isp,
        'history': isp_history
    })


if __name__ == '__main__':
    app.run()
