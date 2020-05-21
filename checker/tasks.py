import os
import schedule, datetime
from celery.decorators import periodic_task
from celery.task.schedules import crontab
import celery
import subprocess
from subprocess import Popen, PIPE
from sitechecker.celery import app

from datetime import timedelta, datetime, timezone
from .models import SiteList, PingInfo

# disable UTC so that Celery can use local time
app.conf.enable_utc = False

def pingsite(hostname):
    process = subprocess.Popen(['ping', '-T', 'tsandaddr', '-c', '5', hostname],
    stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    packetloss = float([x for x in stdout.decode('utf-8').split('\n') if x.find('packet loss') != -1][0].split('%')[0].split(' ')[-1])
    return packetloss

@app.task
def check_interval():
    for site_id in SiteList.objects.values_list('id', flat=True):
        last_run_query = PingInfo.objects.filter(site=site_id).values('date_time')
        interval_query = SiteList.objects.filter(id=site_id).values('interval')
        interval_dict = interval_query.first()
        interval = int(interval_dict['interval'])
        if last_run_query:
            last_run_dict = last_run_query.last()
            last_run = last_run_dict['date_time']
            last_run = last_run.replace(tzinfo=None)
            difference = int(datetime.now().strftime('%M')) - int(last_run.strftime('%M'))
        else:
            difference = 999

        retrieved_site_name = SiteList.objects.get(id=site_id)
        site_to_ping = retrieved_site_name.site_name
        if difference > interval:
            checksite.apply_async(args=(site_to_ping,))

@app.task
def checksite(site_name):
    result = pingsite(site_name)
    if result==0:
        status = 'UP'
    else:
        status = 'DOWN'

    select_id = SiteList.objects.filter(site_name=site_name).values('id')
    new_info = PingInfo.objects.create(status=status,site_id=select_id)
    new_info.save()

app.conf.beat_schedule = {
    "ping-task": {
        "task": "checker.tasks.check_interval",
        "schedule": crontab(minute="*", hour="*")
    }
}



 
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
