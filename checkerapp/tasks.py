# import os
from datetime import datetime

import requests
from celery import shared_task
from celery.task.schedules import crontab
from django.contrib.contenttypes.models import ContentType

from .models import BaseCheck
from .models import CheckResult
from .models import HttpCheck
from sitechecker.celery import app

# from django.core.mail import send_mail

# from .models import PingCheck
# from .models import TcpCheck

# from subprocess import Popen

# disable UTC so that Celery can use local time
app.conf.enable_utc = False


# def check_site(hostname):
#     # response = os.system("ping -c 1 " + hostname)
#     # return response
#     process = subprocess.Popen(
#         ["ping", "-T", "tsandaddr", "-c", "5", hostname], stdout=PIPE, stderr=PIPE
#     )
#     stdout, stderr = process.communicate()
#     packetloss = float(
#         [x for x in stdout.decode("utf-8").split("\n") if x.find("packet loss") != -1][
#             0
#         ]
#         .split("%")[0]
#         .split(" ")[-1]
#     )
#     return packetloss


def check_site(hostname):
    response = requests.get(hostname).status_code
    return response
    # return os.system("curl --write-out %{http_code} --silent --output /dev/null " + hostname)


@shared_task
def check_interval():
    http_type = ContentType.objects.get_for_model(HttpCheck)
    base_checks_http = BaseCheck.objects.filter(
        content_type=http_type, maintenance_mode=False
    )

    for base_check_obj in list(base_checks_http):
        last_run_time = base_check_obj.content_object.results.last().created_at
        interval = base_check_obj.interval
        if last_run_time:
            difference = abs(
                int(datetime.now().strftime("%M")) - int(last_run_time.strftime("%M"))
            )
        else:
            difference = 999

        if difference > interval:
            task_obj = {"base_check_obj": base_check_obj}
            http_check_task.apply_async(args=(task_obj,))


@shared_task
def http_check_task(task_obj):
    result = check_site(task_obj["base_check_obj"].content_object.site_name)
    if result == task_obj["base_check_obj"].content_object.expected_status_code:
        status = 1
    else:
        status = 0

    # http_check_obj = HttpCheck.objects.get(site_name=site_name)
    final_result = CheckResult.objects.create(result=status)
    task_obj["base_check_obj"].content_object.results.add(final_result)
    check_failure.apply_async(args=(task_obj,))


@shared_task
def check_failure(task_obj):
    # http_obj = HttpCheck.objects.get(site_name=site_name)
    backoff_count = task_obj["base_check_obj"].backoff_count
    last_n_failures = list(
        task_obj["base_check_obj"].content_object.results.filter(
            result=CheckResult.FAILURE
        )[:backoff_count]
    )

    if len(last_n_failures) == backoff_count:
        return "Working"
    #     alert_user.apply_async(args=(task_obj,))


# @shared_task
# def alert_user(site_name):
#     http_obj = HttpCheck.objects.get(site_name=site_name)
#     base_check_users = http_obj.base_check.first().users.all()
#     return base_check_users
# # user_list = list(site_info.users.all()) #many-to-many relationship
# if site_info.alert_type == "email":
#     send_email_task.apply_async(args=(site_name,))
# elif site_info.alert_type == "phone":
#     pass
# else:
#     return "failed"


@shared_task
def send_email_task(site_name):
    pass
    # site_info = SiteList.objects.get(site_name=site_name)
    # user_list = list(site_info.users.values_list("email"))
    # send_mail(
    #     "Report from site checker", "Website down", "sahilrajpal05@gmail.com", user_list
    # )
    # return "Sent"


app.conf.beat_schedule = {
    "ping-task": {
        "task": "checkerapp.tasks.check_interval",
        "schedule": crontab(minute="*", hour="*"),
    }
}
