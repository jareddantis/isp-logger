isp-logger
===

This is a web-based application for monitoring and logging ISP data to a database. It is meant for use in multi-WAN environments, where the current ISP might change depending on factors such as load balancing or failover configurations, and is useful for monitoring outages.

# Structure

The application is divided into two parts:

- `query_isp.py`, a Python script that queries the current ISP from [ipinfo.io](https://ipinfo.io) and logs the result to an SQLite3 database called `isp.db`.
- `dashboard.py`, a Python script that instantiates a Flask server for querying the current ISP and displaying historical data in a browser.

`query_isp.py` is meant to be run periodically, and `dashboard.py` is meant to be run as a daemon/always-on process.

# Requirements

This application was wrote for Python 3.9.2, as this is the version that ships with Raspbian OS Bullseye at the time of writing, but it should work with any Python 3.9+ version.

The packages required by the application may be installed using
```
pip install -r requirements.txt
```

Remember to use a virtualenv!

# Running the query script

Run the query script using the command
```
python query_isp.py
```

# Running the dashboard

Although the dashboard only uses static HTML templates, it does make use of TailwindCSS utility classes for styling, which requires generation of the `output.css` file.

Install TailwindCSS according to the [official instructions,](https://tailwindcss.com/docs/installation) and run the following command from the project root directory:

```bash
npx tailwindcss -o static/styles/output.css --minify
```

Append `--watch` to the above command if you want to automatically regenerate the CSS file when you save a change to any of the other HTML, JS, and CSS files in the project.

Running the Flask server process for development, meanwhile, is done through the following command (assuming you are in a virtualenv where `flask` is in `$PATH`):

```
FLASK_APP=dashboard.py FLASK_ENV=development flask run
```

The dashboard can then be accessed at `http://localhost:5000/`.

# License

See LICENSE.md.
