import datetime
import os
import subprocess
from datetime import datetime
from datetime import timedelta
from datetime import timezone
from subprocess import PIPE
from subprocess import Popen

import celery
import schedule
from celery import shared_task
from celery.decorators import periodic_task
from celery.task.schedules import crontab
from django.core.mail import send_mail

from .models import PingInfo
from .models import SiteList
from sitechecker.celery import app

# disable UTC so that Celery can use local time
app.conf.enable_utc = False


def pingsite(hostname):
    # response = os.system("ping -c 1 " + hostname)
    # return response
    process = subprocess.Popen(
        ["ping", "-T", "tsandaddr", "-c", "5", hostname], stdout=PIPE, stderr=PIPE
    )
    stdout, stderr = process.communicate()
    packetloss = float(
        [x for x in stdout.decode("utf-8").split("\n") if x.find("packet loss") != -1][
            0
        ]
        .split("%")[0]
        .split(" ")[-1]
    )
    return packetloss


@shared_task
def check_interval():
    # for site_id in SiteList.objects.values_list('id', flat=True):
    for site_id in (
        SiteList.objects.exclude(maintenance_mode=1)
        .values_list("id", flat=True)
        .order_by("id")
    ):
        last_run_query = PingInfo.objects.filter(site=site_id).values("date_time")
        interval_query = SiteList.objects.filter(id=site_id).values("interval")
        interval_dict = interval_query.first()
        interval = int(interval_dict["interval"])
        if last_run_query:
            last_run_dict = last_run_query.last()
            last_run = last_run_dict["date_time"]
            last_run = last_run.replace(tzinfo=None)
            difference = abs(
                int(datetime.now().strftime("%M")) - int(last_run.strftime("%M"))
            )
        else:
            difference = 999

        retrieved_site_name = SiteList.objects.get(id=site_id)
        site_to_ping = retrieved_site_name.site_name
        if difference > interval:
            checksite.apply_async(args=(site_to_ping,))


@shared_task
def checksite(site_name):
    result = pingsite(site_name)
    if result == 0:
        status = "UP"
    else:
        status = "DOWN"

    select_id = SiteList.objects.filter(site_name=site_name).values("id")
    new_info = PingInfo.objects.create(status=status, site_id=select_id)
    new_info.save()
    check_failure.apply_async(args=(site_name,))


@shared_task
def check_failure(site_name):
    calculated_failure_count = 0
    site_id = SiteList.objects.filter(site_name=site_name).values("id")
    failure_count_query = SiteList.objects.filter(site_name=site_name).values(
        "failure_count"
    )
    failure_count_dict = failure_count_query.first()
    failure_count = failure_count_dict["failure_count"]
    last_n_failures = list(
        PingInfo.objects.filter(site_id__in=site_id).values_list("status")[
            :failure_count
        ]
    )

    for last_status in last_n_failures:
        if last_status[0] == "DOWN":
            calculated_failure_count += 1
        if calculated_failure_count == failure_count:
            alert_user.apply_async(args=(site_name,))


@shared_task
def alert_user(site_name):
    site_info = SiteList.objects.get(site_name=site_name)
    # user_list = list(site_info.users.all()) #many-to-many relationship
    if site_info.alert_type == "email":
        send_email_task.apply_async(args=(site_name,))
    elif site_info.alert_type == "phone":
        pass
    else:
        return "failed"


@shared_task
def send_email_task(site_name):
    site_info = SiteList.objects.get(site_name=site_name)
    user_list = list(site_info.users.values_list("email"))
    send_mail(
        "Report from site checker", "Website down", "sahilrajpal05@gmail.com", user_list
    )
    return "Sent"


app.conf.beat_schedule = {
    "ping-task": {
        "task": "checkerapp.tasks.check_interval",
        "schedule": crontab(minute="*", hour="*"),
    }
}