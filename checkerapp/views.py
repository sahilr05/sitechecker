# from datetime import datetime
# from io import BytesIO
# import xhtml2pdf.pisa as pisa
# from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.paginator import EmptyPage
from django.core.paginator import PageNotAnInteger
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import redirect
from django.shortcuts import render
from django.views import View

from .forms import BaseCheckForm
from .forms import HttpCheckForm
from .forms import PingCheckForm
from .forms import ServiceForm
from .forms import TcpCheckForm
from .models import BaseCheck
from .models import CheckResult
from .models import ContentType
from .models import HttpCheck
from .models import PingCheck
from .models import Service
from .models import TcpCheck
from .tasks import http_check_task
from .tasks import ping_check_task
from .tasks import tcp_check_task
from plugins.sms import send_sms

# from django.views.generic import View
# from .models import BaseCheck
# from django.template.loader import get_template


class MyView(View):
    def get(self, request):
        text = "Hello, World!"
        return HttpResponse(text)


def send_sms_test(request):
    send_sms()
    return HttpResponse("sent sms")


def home(request):
    if request.user.is_authenticated and not request.user.is_superuser:
        user = User.objects.get(id=request.user.id)
        base_checks = BaseCheck.objects.filter(users=user).order_by("id")
        services = []
        for user_base_check in base_checks:
            if user_base_check.service_set.first() in services:
                continue
            services.append(user_base_check.service_set.first())

        context = {"services": services}
        return render(request, "services.html", context)

    services = Service.objects.all().order_by("id")
    context = {"services": services}
    return render(request, "services.html", context)


def service(request, pk):
    service_obj = Service.objects.get(id=pk)
    http_type = ContentType.objects.get_for_model(HttpCheck)
    http_checks_info = service_obj.checks.filter(
        content_type=http_type, users=request.user
    ).order_by("id")

    ping_type = ContentType.objects.get_for_model(PingCheck)
    ping_checks_info = service_obj.checks.filter(
        content_type=ping_type, users=request.user
    ).order_by("id")

    tcp_type = ContentType.objects.get_for_model(TcpCheck)
    tcp_checks_info = service_obj.checks.filter(
        content_type=tcp_type, users=request.user
    ).order_by("id")

    context = {
        "service": service_obj,
        "http_checks": http_checks_info,
        "ping_checks": ping_checks_info,
        "tcp_checks": tcp_checks_info,
    }
    return render(request, "service_checks.html", context)


def add_service(request):
    if not request.user.is_superuser:
        return redirect("checkerapp:home")

    if request.method == "POST":
        form = ServiceForm(request.POST)
        if form.is_valid():
            service_name = form.cleaned_data.get("name")
            service_obj = Service.objects.create(name=service_name)
            messages.success(request, f" {service_name} created !!")
            return redirect("checkerapp:service", pk=service_obj.pk)

    form = ServiceForm()
    context = {"form": form}
    return render(request, "add_service.html", context)


def edit_service(request, service_pk):
    if not request.user.is_superuser:
        return redirect("checkerapp:home")

    flag = True
    service_obj = Service.objects.get(id=service_pk)

    form = ServiceForm(request.POST or None, instance=service_obj)
    if form.is_valid():
        service_name = form.cleaned_data.get("name")
        service_obj = Service.objects.filter(id=service_pk).update(name=service_name)
        messages.success(request, f" {service_name} updated !!")
        return redirect("checkerapp:home")

    context = {"form": form, "flag": flag}
    return render(request, "add_service.html", context)


def delete_service(request, service_pk):
    service_obj = Service.objects.get(id=service_pk)
    base_checks = service_obj.checks.all()
    for checks in base_checks:
        checks.content_object.delete()
    service_obj.delete()
    messages.success(request, f" {service_obj.name} deleted !!")
    return redirect("checkerapp:home")


def http_info(request, pk):
    http_results_obj = HttpCheck.objects.get(id=pk)  # fetch site name from HttpCheck
    base_check_obj = (
        http_results_obj.base_check.first()
    )  # fetch interval, backoff count, etc.
    result = http_results_obj.results.all().order_by("id")  # fetch status (UP/DOWN)
    user_list = base_check_obj.users.all()
    all_users = User.objects.all()
    last_down_time = http_results_obj.results.filter(result=CheckResult.FAILURE).last()

    page = request.GET.get("page", 1)
    paginator = Paginator(result, 10)

    try:
        result = paginator.page(page)
    except PageNotAnInteger:
        result = paginator.page(1)
    except EmptyPage:
        result = paginator.page(paginator.num_pages)

    context = {
        "result": result,
        "last_down_time": last_down_time,
        "site": http_results_obj,
        "base_check": base_check_obj,
        "user_list": user_list,
        "all_users": all_users,
    }
    return render(request, "check_info/http_info.html", context)


def ping_info(request, pk):
    ping_results_obj = PingCheck.objects.get(id=pk)
    base_check_obj = ping_results_obj.base_check.first()
    result = ping_results_obj.results.all().order_by("id")
    user_list = base_check_obj.users.all()
    all_users = User.objects.all()
    last_down_time = ping_results_obj.results.filter(result=CheckResult.FAILURE).last()

    page = request.GET.get("page", 1)
    paginator = Paginator(result, 10)

    try:
        result = paginator.page(page)
    except PageNotAnInteger:
        result = paginator.page(1)
    except EmptyPage:
        result = paginator.page(paginator.num_pages)

    context = {
        "result": result,
        "ip_address": ping_results_obj,
        "base_check": base_check_obj,
        "user_list": user_list,
        "all_users": all_users,
        "last_down_time": last_down_time,
    }
    return render(request, "check_info/ping_info.html", context)


def tcp_info(request, pk):
    tcp_results_obj = TcpCheck.objects.get(id=pk)
    base_check_obj = tcp_results_obj.base_check.first()
    result = tcp_results_obj.results.all().order_by("id")
    user_list = base_check_obj.users.all()
    all_users = User.objects.all()
    last_down_time = tcp_results_obj.results.filter(result=CheckResult.FAILURE).last()

    page = request.GET.get("page", 1)
    paginator = Paginator(result, 10)

    try:
        result = paginator.page(page)
    except PageNotAnInteger:
        result = paginator.page(1)
    except EmptyPage:
        result = paginator.page(paginator.num_pages)

    context = {
        "result": result,
        "ip_address": tcp_results_obj,
        "base_check": base_check_obj,
        "user_list": user_list,
        "all_users": all_users,
        "last_down_time": last_down_time,
    }
    return render(request, "check_info/tcp_info.html", context)


def add_http_check(request, service_pk):
    if request.method == "POST":
        http_check_form = HttpCheckForm(request.POST)
        base_check_form = BaseCheckForm(request.POST)
        if http_check_form.is_valid() and base_check_form.is_valid():
            site_name = http_check_form.cleaned_data.get("site_name")
            expected_status_code = http_check_form.cleaned_data.get(
                "expected_status_code"
            )
            http_check = HttpCheck.objects.create(
                site_name=site_name, expected_status_code=expected_status_code
            )
            interval = base_check_form.cleaned_data.get("interval")
            backoff_count = base_check_form.cleaned_data.get("backoff_count")
            alert_type = base_check_form.cleaned_data.get("alert_type")
            severe_level = base_check_form.cleaned_data.get("severe_level")
            service_obj = Service.objects.get(id=service_pk)
            creator = User.objects.get(id=request.user.pk)
            http_base_check_obj = http_check.base_check.create(
                interval=interval,
                backoff_count=backoff_count,
                alert_type=alert_type,
                severe_level=severe_level,
                creator=creator,
            )
            http_base_check_obj.users.add(creator)
            service_obj.checks.add(http_base_check_obj)
            task_obj = {"base_check_obj": http_base_check_obj}
            http_check_task.apply_async(args=(task_obj,))
            messages.success(request, f" {site_name} created !!")
            return redirect("checkerapp:service", pk=service_pk)

    if not request.user.is_superuser:
        return redirect("checkerapp:service", pk=service_pk)
    http_check_form = HttpCheckForm()
    base_check_form = BaseCheckForm()
    context = {
        "http_check_form": http_check_form,
        "base_check_form": base_check_form,
        "service": Service.objects.get(id=service_pk),
    }
    return render(request, "add_check/add_http_check.html", context)


def edit_http_check(request, service_pk, http_pk):
    flag = True
    http_check_obj = HttpCheck.objects.get(id=http_pk)
    base_check_obj = http_check_obj.base_check.first()
    http_check_form = HttpCheckForm(request.POST or None, instance=http_check_obj)
    base_check_form = BaseCheckForm(request.POST or None, instance=base_check_obj)
    if http_check_form.is_valid() and base_check_form.is_valid():
        site_name = http_check_form.cleaned_data.get("site_name")
        expected_status_code = http_check_form.cleaned_data.get("expected_status_code")
        HttpCheck.objects.filter(id=http_pk).update(
            site_name=site_name, expected_status_code=expected_status_code
        )
        interval = base_check_form.cleaned_data.get("interval")
        backoff_count = base_check_form.cleaned_data.get("backoff_count")
        alert_type = base_check_form.cleaned_data.get("alert_type")
        severe_level = base_check_form.cleaned_data.get("severe_level")
        BaseCheck.objects.filter(id=base_check_obj.id).update(
            interval=interval,
            backoff_count=backoff_count,
            alert_type=alert_type,
            severe_level=severe_level,
        )
        messages.success(request, f" {site_name} updated !!")
        return redirect("checkerapp:service", pk=service_pk)

    context = {
        "flag": flag,
        "http_check_form": http_check_form,
        "base_check_form": base_check_form,
        "service": Service.objects.get(id=service_pk),
    }
    return render(request, "add_check/add_http_check.html", context)


def add_ping_check(request, service_pk):
    if request.method == "POST":
        ping_check_form = PingCheckForm(request.POST)
        base_check_form = BaseCheckForm(request.POST)
        if ping_check_form.is_valid() and base_check_form.is_valid():
            ip_address = ping_check_form.cleaned_data.get("ip_address")
            ping_check = PingCheck.objects.create(ip_address=ip_address)
            interval = base_check_form.cleaned_data.get("interval")
            backoff_count = base_check_form.cleaned_data.get("backoff_count")
            alert_type = base_check_form.cleaned_data.get("alert_type")
            severe_level = base_check_form.cleaned_data.get("severe_level")
            service_obj = Service.objects.get(id=service_pk)
            creator = User.objects.get(id=request.user.pk)
            ping_base_check_obj = ping_check.base_check.create(
                interval=interval,
                backoff_count=backoff_count,
                alert_type=alert_type,
                severe_level=severe_level,
                creator=creator,
            )
            ping_base_check_obj.users.add(creator)
            service_obj.checks.add(ping_base_check_obj)
            task_obj = {"base_check_obj": ping_base_check_obj}
            ping_check_task.apply_async(args=(task_obj,))
            messages.success(request, f" {ip_address} created !!")
            return redirect("checkerapp:service", pk=service_pk)

    if not request.user.is_superuser:
        return redirect("checkerapp:service", pk=service_pk)
    ping_check_form = PingCheckForm()
    base_check_form = BaseCheckForm()
    context = {
        "ping_check_form": ping_check_form,
        "base_check_form": base_check_form,
        "service": Service.objects.get(id=service_pk),
    }
    return render(request, "add_check/add_ping_check.html", context)


def edit_ping_check(request, service_pk, ping_pk):
    flag = True
    ping_check_obj = PingCheck.objects.get(id=ping_pk)
    base_check_obj = ping_check_obj.base_check.first()
    ping_check_form = PingCheckForm(request.POST or None, instance=ping_check_obj)
    base_check_form = BaseCheckForm(request.POST or None, instance=base_check_obj)
    if ping_check_form.is_valid() and base_check_form.is_valid():
        ip_address = ping_check_form.cleaned_data.get("ip_address")
        PingCheck.objects.filter(id=ping_pk).update(ip_address=ip_address)
        interval = base_check_form.cleaned_data.get("interval")
        backoff_count = base_check_form.cleaned_data.get("backoff_count")
        alert_type = base_check_form.cleaned_data.get("alert_type")
        severe_level = base_check_form.cleaned_data.get("severe_level")

        BaseCheck.objects.filter(id=base_check_obj.id).update(
            interval=interval,
            backoff_count=backoff_count,
            alert_type=alert_type,
            severe_level=severe_level,
        )
        messages.success(request, f" {ip_address} updated !!")
        return redirect("checkerapp:service", pk=service_pk)

    context = {
        "flag": flag,
        "ping_check_form": ping_check_form,
        "base_check_form": base_check_form,
        "service": Service.objects.get(id=service_pk),
    }
    return render(request, "add_check/add_ping_check.html", context)


def add_tcp_check(request, service_pk):
    if request.method == "POST":
        tcp_check_form = TcpCheckForm(request.POST)
        base_check_form = BaseCheckForm(request.POST)
        if tcp_check_form.is_valid() and base_check_form.is_valid():
            ip_address = tcp_check_form.cleaned_data.get("ip_address")
            tcp_check = TcpCheck.objects.create(ip_address=ip_address)
            interval = base_check_form.cleaned_data.get("interval")
            backoff_count = base_check_form.cleaned_data.get("backoff_count")
            alert_type = base_check_form.cleaned_data.get("alert_type")
            severe_level = base_check_form.cleaned_data.get("severe_level")
            service_obj = Service.objects.get(id=service_pk)
            creator = User.objects.get(id=request.user.pk)
            tcp_base_check_obj = tcp_check.base_check.create(
                interval=interval,
                backoff_count=backoff_count,
                alert_type=alert_type,
                severe_level=severe_level,
                creator=creator,
            )
            tcp_base_check_obj.users.add(creator)
            service_obj.checks.add(tcp_base_check_obj)
            task_obj = {"base_check_obj": tcp_base_check_obj}
            tcp_check_task.apply_async(args=(task_obj,))
            messages.success(request, f" {ip_address} created !!")
            return redirect("checkerapp:service", pk=service_pk)

    if not request.user.is_superuser:
        return redirect("checkerapp:service", pk=service_pk)
    tcp_check_form = TcpCheckForm()
    base_check_form = BaseCheckForm()
    context = {
        "tcp_check_form": tcp_check_form,
        "base_check_form": base_check_form,
        "service": Service.objects.get(id=service_pk),
    }
    return render(request, "add_check/add_tcp_check.html", context)


def edit_tcp_check(request, service_pk, tcp_pk):
    flag = True
    tcp_check_obj = TcpCheck.objects.get(id=tcp_pk)
    base_check_obj = tcp_check_obj.base_check.first()
    tcp_check_form = TcpCheckForm(request.POST or None, instance=tcp_check_obj)
    base_check_form = BaseCheckForm(request.POST or None, instance=base_check_obj)
    if tcp_check_form.is_valid() and base_check_form.is_valid():
        ip_address = tcp_check_form.cleaned_data.get("ip_address")
        TcpCheck.objects.filter(id=tcp_pk).update(ip_address=ip_address)
        interval = base_check_form.cleaned_data.get("interval")
        backoff_count = base_check_form.cleaned_data.get("backoff_count")
        alert_type = base_check_form.cleaned_data.get("alert_type")
        severe_level = base_check_form.cleaned_data.get("severe_level")
        BaseCheck.objects.filter(id=base_check_obj.id).update(
            interval=interval,
            backoff_count=backoff_count,
            alert_type=alert_type,
            severe_level=severe_level,
        )
        messages.success(request, f" {ip_address} updated !!")
        return redirect("checkerapp:service", pk=service_pk)

    context = {
        "flag": flag,
        "tcp_check_form": tcp_check_form,
        "base_check_form": base_check_form,
        "service": Service.objects.get(id=service_pk),
    }
    return render(request, "add_check/add_tcp_check.html", context)


def maintenance(request, service_type_id, service_pk, pk):
    selected_service_type = (
        BaseCheck.objects.filter(content_type_id=service_type_id).first().content_type
    )
    service_obj = BaseCheck.objects.get(
        object_id=pk, content_type=selected_service_type
    )
    maintenance_status = service_obj.maintenance_mode
    if maintenance_status:
        service_obj.maintenance_mode = False
    else:
        service_obj.maintenance_mode = True

    service_obj.save()

    return redirect("checkerapp:service", pk=service_pk)


def delete_check(request, service_type_id, service_pk, pk):
    selected_service_type = (
        BaseCheck.objects.filter(content_type_id=service_type_id).first().content_type
    )
    service_obj = BaseCheck.objects.get(
        object_id=pk, content_type=selected_service_type
    )
    service_obj.content_object.delete()

    return redirect("checkerapp:service", pk=service_pk)

    # if request.user.is_authenticated and not request.user.is_superuser:
    #     user = User.objects.get(id=request.user.id)
    #     # site_names = user.sitelist_users.all()
    #     return render(request, "home.html")

    # http_checks = HttpCheck.objects.all().order_by("id")
    # base_checks=[]
    # for site in http_checks:
    #     http_base_check = site.base_check.first()
    #     base_checks.append(http_base_check)

    # http_check_info = zip(http_checks, base_checks)
    # context = {
    #         'http_checks_info': http_check_info,
    #     }
    # return render(request, "home.html", context)


# @login_required


# @login_required
# def edit_site(request, pk):
#     if not request.user.is_superuser:
#         return redirect("checkerapp:home")
#     site = SiteList.objects.get(id=pk)
#     form = SiteForm(request.POST or None, instance=site)
#     if form.is_valid():
#         site_name = form.cleaned_data.get("site_name")
#         interval = form.cleaned_data.get("interval")
#         alert_type = form.cleaned_data.get("alert_type")
#         failure_count = form.cleaned_data.get("failure_count")
#         site = SiteList.objects.filter(id=pk).update(
#             site_name=site_name,
#             alert_type=alert_type,
#             interval=interval,
#             failure_count=failure_count,
#             admin=User.objects.get(id=request.user.pk),
#         )
#         return redirect("checkerapp:home")
#     return render(request, "edit_site.html", {"form": form})


# @login_required
# def add_site(request):
#     if request.method == "POST":
#         form = SiteForm(request.POST)
#         if form.is_valid():
#             site_name = form.cleaned_data.get("site_name")
#             interval = form.cleaned_data.get("interval")
#             failure_count = form.cleaned_data.get("failure_count")
#             alert_type = form.cleaned_data.get("alert_type")
#             site = SiteList.objects.create(
#                 site_name=site_name,
#                 # ping -c1 justkart.com | sed -nE 's/^PING[^(]+\(([^)]+)\).*/\1/p'
#                 alert_type=alert_type,
#                 interval=interval,
#                 failure_count=failure_count,
#                 admin=User.objects.get(id=request.user.pk),
#             )
#             site.save()
#             return redirect("checkerapp:home")

#     if not request.user.is_superuser:
#         return redirect("checkerapp:home")
#     form = SiteForm()
#     return render(request, "add_site.html", context={"form": form})


# @login_required
# def delete_user(request, pk):
#     user_to_delete = User.objects.get(id=pk)
#     user_to_delete.delete()
#     return redirect("user_list")


# @login_required
# def delete_site(request, pk):
#     site_to_delete = SiteList.objects.get(id=pk)
#     site_to_delete.delete()
#     return redirect("checkerapp:home")


# @login_required
# def maintenance(request, pk):
#     site = SiteList.objects.get(id=pk)
#     maintenance_status = site.maintenance_mode
#     if maintenance_status == 1:
#         site.maintenance_mode = 0
#     else:
#         site.maintenance_mode = 1
#     site.save()
#     return redirect("checkerapp:home")


# class RenderPDF:
#     @staticmethod
#     def render(path: str, params: dict):
#         template = get_template(path)
#         html = template.render(params)
#         response = BytesIO()
#         pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), response)
#         if not pdf.err:
#             return HttpResponse(response.getvalue(), content_type="application/pdf")


# class Pdf(View):
#     def get(self, request, pk):

#         ping_report_obj = PingInfo.objects.filter(site_id=pk).order_by("-date_time")
#         site_list_obj = SiteList.objects.get(id=pk)

#         last_down_time = (
#             ping_report_obj.filter(status="DOWN").order_by("-date_time").first()
#         )
#         today = datetime.now()

#         params = {
#             "today": today,
#             "site_name": site_list_obj,
#             "last_down_time": last_down_time,
#             "result": ping_report_obj,
#             "request": request,
#         }
#         return RenderPDF.render("pdf.html", params)
