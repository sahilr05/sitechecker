# Sitechecker

* A Web interface that allows you to monitor services
* Alerts if those services start misbehaving or go down
* Provides extensible plugin functionality to create separate alerting and monitoring modules
* Dockerised stateless workers which can be scaled as required based on number of monitoring checks
* Manage Celery workers to distribute tasks according to number of service checks

### [Why should I use all checks ?](https://www.rapidspike.com/kb/ping-vs-tcp-vs-http-monitors/)

## Types of checks
1. HTTP Checks:
Checks for existence of pages for monitored website. 

2. Ping Checks:
Sends 5 ICMP packets to host IP address and waits for response using which determines whether address is available over a network or not

3. TCP Checks:
Checks whether host is accessible on given port on the network device or not

## Types of severity
1. Warning Severity: [One alert per day](https://github.com/sahilr05/sitechecker/blob/c30675001dbb3bc6317399bfb2d99e3fb22a401f/checkerapp/tasks.py#L177)

2. Critical Severity:  [One alert per hour](https://github.com/sahilr05/sitechecker/blob/c30675001dbb3bc6317399bfb2d99e3fb22a401f/checkerapp/tasks.py#L171)

## Quickstart

By default sitechecker doesn't comes with any plugin preinstalled

```
git clone git@github.com:sahilr05/sitechecker.git
```

* Add your keys in ```.env``` using ```.env.example``` as template
```
cp .env.example .env
make up
```

open new terminal window and create superuser 

```
make login-web
python manage.py createsuperuser
```

use the same username and password to login into portal

## Running locally in virtual environment

* Setup and activate virtual environment
```
virtualenv -p python3.8 venv        
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

* Open new terminal tab and start redis server
```
sudo redis-server
```

* Execute following command to trigger celery workers
```
celery -A sitechecker worker -l info -Q check_queue 
celery -A sitechecker worker -l info -Q alert_queue
celery -A sitechecker beat -l info
```

## Adding plugins
[Telegram Plugin](https://github.com/sahilr05/sitechecker-telegram-plugin)

[Plugin Example](https://github.com/sahilr05/sitechecker-generic-plugin)

1. Run the following command after adding plugin
```
python manage.py runscript add_plugin
```
2. Run the following command after removing plugin
```
python manage.py runscript remove_plugin
```
