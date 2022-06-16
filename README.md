isp-logger
===

This is a web-based application for monitoring and logging ISP data to a database. It is meant for use in multi-WAN environments, where the current ISP might change depending on factors such as load balancing or failover configurations, and is useful for monitoring outages.

## Structure

The application is divided into two parts:

- `query_isp.py`, a Python script that queries the current ISP from [ipinfo.io](https://ipinfo.io) and logs the result to an SQLite3 database called `isp.db`.
- `dashboard.py`, a Python script that instantiates a Flask server for querying the current ISP and displaying historical data in a browser.

Both parts are meant to be run as daemon/always-on processes.

## Requirements

This application was written for Python 3.9.2, as this is the version that ships with Raspbian OS Bullseye at the time of writing, but it should work with any Python 3.9+ version.

The packages required by the application may be installed using
```
pip install -r requirements.txt
```

Remember to use a virtualenv!

## Running the query script

Run the query script using the command
```
python query_isp.py
```

If you installed the project requirements in a virtualenv, you might want to create a wrapper script for activating the virtualenv and running the script, like this...
```bash
#!/bin/bash

# Change to the project directory
cd "${0%/*}"

# Activate virtualenv in .venv under project directory
# Change .venv to your virtualenv directory as necessary
source .venv/bin/activate

# Run dashboard
PYTHONUNBUFFERED=1 python query_isp.py

# Cleanup
deactivate
exit 0
```

...and creating a systemd script to run the wrapper script in the background, like this:
```
[Unit]
Description=isp-logger daemon
Wants=network-online.target
After=network-online.target

[Service]
ExecStart=/path/to/project/run-query.sh
WorkingDirectory=/path/to/project
User=<your username>

[Install]
WantedBy=multi-user.target
```

## Running the dashboard

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

Like the query script, the dashboard is meant to be run automatically, so you might want to create a wrapper script that enters the virtualenv and passes the right arguments to the server for you:
```bash
#!/bin/bash

# Change to the project directory
cd "${0%/*}"

# Activate virtualenv
source .venv/bin/activate

# Run dashboard
PYTHONUNBUFFERED=1 FLASK_APP=dashboard.py flask run --host=0.0.0.0

# Cleanup
deactivate
exit 0
```

You might also want to create a systemd service (or something similar for non-Debian systems) to run the Flask server as a daemon:

```
[Unit]
Description=isp-logger dashboard
Wants=network-online.target
After=network-online.target

[Service]
ExecStart=/path/to/project/run-dashboard.sh
WorkingDirectory=/path/to/project
User=<your username>

[Install]
WantedBy=multi-user.target
```

### License

See LICENSE.md.
