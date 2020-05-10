import os
import schedule, datetime
from celery.decorators import periodic_task
from celery.task.schedules import crontab
# from celery.schedules import crontab
from datetime import timedelta
import celery
import subprocess
from subprocess import Popen, PIPE

from sitechecker.celery import app

# disable UTC so that Celery can use local time
app.conf.enable_utc = False

def pingsite(hostname):
    process = subprocess.Popen(['ping', '-T', 'tsandaddr', '-c', '5', hostname],
    stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    packetloss = float([x for x in stdout.decode('utf-8').split('\n') if x.find('packet loss') != -1][0].split('%')[0].split(' ')[-1])
    return packetloss
 
    # response = os.system("ping -T tsandaddr -c 5  " + hostname)

# @app.task
# val = app.conf.beat_schedule = {
#     "ping-task": {
#         "task": "checker.tasks.pingsite",
#         "schedule": crontab(hour="*", minute="*")
#     }
# }
    # response = urllib.request.urlopen(hostname).getcode()
# A periodic task that will run every minute (the symbol "*" means every)
# @periodic_task(run_every=(crontab(hour="*", minute="*", day_of_week="*")))
