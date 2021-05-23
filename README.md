# Sitechecker

* A Web interface that allows you to monitor services
* Alerts if those services start misbehaving or go down
* Provides extensible plugin functionality to create separate alerting and monitoring modules
* Dockerised stateless workers which can be scaled as required based on number of monitoring checks
* Manage Celery workers to distribute tasks according to number of service checks

### [Why should I use all checks ?](https://www.rapidspike.com/kb/ping-vs-tcp-vs-http-monitors/)

## Types of checks
1. **HTTP Checks**:
Sends HTTP GET request and compares expected response status code.

2. **Ping Checks**:
Sends ICMP echo request packets to the target host waiting for an ICMP echo reply to check whether the host is reachable or not.

3. **TCP Checks**:
Attempts to establish TCP connection to the mentioned host and port.

If mismatch happens for more than back-off count then alerts are sent to registered users of respective service

## Types of severity
1. Warning Severity: [One alert per day](https://github.com/sahilr05/sitechecker/blob/c30675001dbb3bc6317399bfb2d99e3fb22a401f/checkerapp/tasks.py#L177)

2. Critical Severity:  [One alert per hour](https://github.com/sahilr05/sitechecker/blob/c30675001dbb3bc6317399bfb2d99e3fb22a401f/checkerapp/tasks.py#L171)

## Quickstart

#### Note: By default sitechecker doesn't comes with any plugin preinstalled
* Clone this repo
* Add your keys in ```.env``` using ```.env.example``` as template
```
cp .env.example .env
make up
```

* Open new terminal window and create superuser
```
make login-web
python manage.py createsuperuser
```

Use the same username and password to login into portal

## Running locally in virtual environment

* Setup and activate virtual environment
```
virtualenv -p python3.x venv
source venv/bin/activate
```

* Install requirements
```
pip install poetry
poetry install
```

* Perform migrations
```
python manage.py migrate
```

* Create superuser
```
python manage.py createsuperuser
```

* Use the same username and password to login into portal
```
python manage.py runserver
```

* Make sure redis is running and listening on the address mentioned in .env
```
sudo redis-server
```

* Execute following commands to trigger celery workers
```
celery -A sitechecker worker -l info -Q check_queue
celery -A sitechecker worker -l info -Q alert_queue
celery -A sitechecker beat -l info
```

## Adding plugins
Checkout [Telegram Plugin](https://github.com/sahilr05/sitechecker-telegram-plugin) made using [Python Telegram Bot](https://python-telegram-bot.readthedocs.io/en/stable/)

Refer [Alert Plugin Example](https://github.com/sahilr05/sitechecker-generic-plugin) to create custom plugins

1. Run the following command after adding plugin
```
python manage.py runscript add_plugin
```
2. Run the following command after removing plugin
```
python manage.py runscript remove_plugin
```
