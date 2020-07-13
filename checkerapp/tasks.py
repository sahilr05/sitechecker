import subprocess
from datetime import datetime
from subprocess import PIPE

import requests
from celery import shared_task
from celery.task.schedules import crontab
from django.contrib.contenttypes.models import ContentType

from .models import AlertPlugin
from .models import AlertSent
from .models import BaseCheck
from .models import CheckResult
from .models import HttpCheck
from .models import PingCheck
from .utils import check_tcp
from sitechecker.celery import app

# from plugins.sms import send_sms

# from django.http import HttpResponse


# from .models import TcpCheck

# disable UTC so that Celery can use local time
app.conf.enable_utc = False


def check_site(hostname):
    try:
        response = requests.get(hostname).status_code
    except:  # noqa
        response = 0
    return response


# To capture error :
# except Exception as e:
#     print(e)


def ping_ip(ip_address):
    process = subprocess.Popen(
        ["ping", "-c", "5", ip_address], stdout=PIPE, stderr=PIPE
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
    base_checks = BaseCheck.objects.filter(maintenance_mode=False)

    for base_check_obj in list(base_checks):
        try:
            last_run_time = base_check_obj.content_object.results.last().created_at
            difference = abs(
                int(datetime.now().strftime("%M")) - int(last_run_time.strftime("%M"))
            )
        except Exception:
            difference = 999

        interval = base_check_obj.interval - 1
        if difference > interval:
            task_obj = {"base_check_obj": base_check_obj}
            http_type = ContentType.objects.get_for_model(HttpCheck)
            ping_type = ContentType.objects.get_for_model(PingCheck)
            # tcp_type = ContentType.objects.get_for_model(TcpCheck)
            if base_check_obj.content_type == http_type:
                http_check_task.apply_async(args=(task_obj,))
            elif base_check_obj.content_type == ping_type:
                ping_check_task.apply_async(args=(task_obj,))
            else:
                tcp_check_task.apply_async(args=(task_obj,))


@shared_task
def http_check_task(task_obj):
    result = check_site(task_obj["base_check_obj"].content_object.site_name)
    if result == task_obj["base_check_obj"].content_object.expected_status_code:
        status = 1
    else:
        status = 0

    final_result = CheckResult.objects.create(result=status)
    task_obj["base_check_obj"].content_object.results.add(final_result)
    check_failure.apply_async(args=(task_obj,))


@shared_task
def ping_check_task(task_obj):
    result = ping_ip(task_obj["base_check_obj"].content_object.ip_address)
    if result > 70:
        status = 1
    else:
        status = 0

    final_result = CheckResult.objects.create(result=status)
    task_obj["base_check_obj"].content_object.results.add(final_result)
    check_failure.apply_async(args=(task_obj,))


@shared_task
def tcp_check_task(task_obj):
    ip_address = task_obj["base_check_obj"].content_object.ip_address
    port = task_obj["base_check_obj"].content_object.port
    result = check_tcp(ip_address, port)

    if result:
        status = 1
    else:
        status = 0

    final_result = CheckResult.objects.create(result=status)
    task_obj["base_check_obj"].content_object.results.add(final_result)
    check_failure.apply_async(args=(task_obj,))


@shared_task
def check_failure(task_obj):
    backoff_count = task_obj["base_check_obj"].backoff_count
    last_n_failures = list(
        task_obj["base_check_obj"]
        .content_object.results.all()
        .order_by("-id")[:backoff_count]
    )
    failure_count = 0
    for result_obj in last_n_failures:
        if result_obj.result == 0:
            failure_count += 1
    if failure_count >= backoff_count:
        # return "Working"
        check_severity.apply_async(args=(task_obj,))


def last_alert_date_check(task_obj):
    check_obj = task_obj["base_check_obj"]
    try:
        last_alert_date = int(
            AlertSent.objects.filter(check_obj=check_obj).last().sent_at.strftime("%d")
        )
    except Exception:
        last_alert_date = 00
    return last_alert_date


def last_alert_hour_check(task_obj):
    check_obj = task_obj["base_check_obj"]
    try:
        last_alert_hour = int(
            AlertSent.objects.filter(check_obj=check_obj).last().sent_at.strftime("%H")
        )
    except Exception:
        last_alert_hour = 00
    return last_alert_hour


@shared_task
def critical_severity(task_obj):
    # if int(datetime.now().strftime("%H")) > last_alert_hour_check(task_obj):
    check_obj = task_obj["base_check_obj"]
    service_obj = check_obj.service_set.first()
    service_plugins = list(service_obj.critical_severity.values_list("name", flat=True))
    installed_plugins = [cls for cls in AlertPlugin.__subclasses__()]

    for plugin in installed_plugins:
        if plugin.__name__ in service_plugins:
            plugin.send_alert_task.apply_async(args=(task_obj,))


@shared_task
def warning_severity(task_obj):
    # if int(datetime.now().strftime("%d")) > last_alert_date_check(task_obj):
    check_obj = task_obj["base_check_obj"]
    service_obj = check_obj.service_set.first()
    service_plugins = list(service_obj.warning_severity.values_list("name", flat=True))
    installed_plugins = [cls for cls in AlertPlugin.__subclasses__()]

    for plugin in installed_plugins:
        if plugin.__name__ in service_plugins:
            plugin.send_alert_task.apply_async(args=(task_obj,))


@shared_task
def check_severity(task_obj):
    check_obj = task_obj["base_check_obj"]
    if check_obj.severe_level == 0:  # warning
        warning_severity.apply_async(args=(task_obj,))

    elif check_obj.severe_level == 1:  # critical
        critical_severity.apply_async(args=(task_obj,))

    else:  # nothing.. remove later
        pass


app.conf.beat_schedule = {
    "ping-task": {
        "task": "checkerapp.tasks.check_interval",
        "schedule": crontab(minute="*", hour="*"),
    }
}

# @shared_task
# def send_email_task(task_obj):
#     # return "email"
#     check_obj = task_obj["base_check_obj"]
#     # if int(datetime.now().strftime("%d")) > last_alert_date_check(task_obj):
#     user_list = list(check_obj.service_set.first().users.values_list("email"))
#     # user_list = [("vuuxq97686@klefv6.com",)]
#     # return HttpResponse(user_list)
#     send_mail(
#         "Report from site checker", "Website down", "sahilrajpal05@gmail.com", user_list
#     )
#     AlertSent.objects.create(check_obj=check_obj)
#     return "Email sent !"


# def normal_severity(task_obj):
#     if int(datetime.now().strftime("%d")) > last_alert_date_check(task_obj):
#         send_email_task.apply_async(args=(task_obj,))
#     try:
#         plugins_obj = [cls for cls in AlertPlugin.__subclasses__()]
#         for plugin in plugins_obj:
#             if plugin.severe_level == 0:
#                 plugin.send_alert_task(task_obj)
#     except Exception:
#         pass


# def warning_severity(task_obj):
#     # check_obj = task_obj["base_check_obj"]
#     if int(datetime.now().strftime("%d")) > last_alert_date_check(task_obj):
#         send_email_task.apply_async(args=(task_obj,))
#         # send_sms_task.apply_async(args=(task_obj,))
#         try:
#             plugins_obj = [cls for cls in AlertPlugin.__subclasses__()]
#             for plugin in plugins_obj:
#                 if plugin.severe_level == 1:
#                     plugin.send_alert_task(task_obj)
#         except Exception:
#             pass


# def critical_severity(task_obj):
#     # check_obj = task_obj["base_check_obj"]
#     if int(datetime.now().strftime("%d")) > last_alert_date_check(task_obj):
#         send_email_task.apply_async(args=(task_obj,))

#     if int(datetime.now().strftime("%H")) > last_alert_hour_check(task_obj):
#         # send_sms_task.apply_async(args=(task_obj,))
#         try:
#             plugins_obj = [cls for cls in AlertPlugin.__subclasses__()]
#             for plugin in plugins_obj:
#                 if plugin.severe_level == 2:
#                     plugin.send_alert_task(task_obj)
#         except Exception:
#             pass


# @shared_task
# def send_sms_task(task_obj):
#     # return "sms"
#     for user in list(task_obj["base_check_obj"].service_set.first().users.all()):
#         message = str(task_obj["base_check_obj"].content_object) + " is down"
#         send_sms(message, user)
#         AlertSent.objects.create(check_obj=task_obj["base_check_obj"])

# send_tg_alert_task.apply_async(args=(task_obj,))   #for testing


# def check_custom_plugins(task_obj):
#     check_obj = task_obj["base_check_obj"]
#     try:
#         plugins_obj = [cls for cls in AlertPlugin.__subclasses__()]
#         for plugin in plugins_obj:
#             if plugin.severe_level == 0: #normal
#                 normal_severity(task_obj)
#             elif plugin.severe_level == 1:
#                 warning_severity(task_obj)
#             else:
#                 critical_severity(task_obj)

#     except Exception:
#         pass
#     return 'check_custom_plugin'


# @shared_task
# def alert_user(task_obj):
#     if task_obj["base_check_obj"].alert_type == 0:  # email
#         send_email_task.apply_async(args=(task_obj,))
#     elif task_obj["base_check_obj"].alert_type == 1:  # telegram
#         send_tg_alert_task.apply_async(args=(task_obj,))
#         return "Telegram"
#     else:  # sms
#         send_sms_task.apply_async(args=(task_obj,))


# @shared_task
# def send_tg_alert_task(task_obj):
#     check_obj = task_obj["base_check_obj"]
#     message = str(check_obj.content_object) + " is down"
#     users = list(
#         AlertPlugin.objects.filter(
#             Q(telegramalertplugin__check_obj=check_obj)
#         ).values_list("alert_receiver")
#     )
#     for user_id in users:
#         telegram_user_obj = TelegramAlertPlugin.objects.filter(
#             Q(alert_receiver=user_id) & Q(check_obj=check_obj)
#         ).first()
#         send_alert(message, telegram_user_obj)
#         AlertSent.objects.create(check_obj=check_obj)
#         return "Success !"

# for user in list(task_obj["base_check_obj"].users.all()):
# for x in AlertPlugin.objects.filter( Q(TelegramAlertPlugin__alert_receiver=user)):
#     print(x.telegram_id)
# for x in AlertPlugin.objects.filter( Q(TelegramAlertPlugin__alert_receiver=user)):
#     print(x.telegram_id)
