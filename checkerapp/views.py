from datetime import datetime
from io import BytesIO

import xhtml2pdf.pisa as pisa
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import EmptyPage
from django.core.paginator import PageNotAnInteger
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import redirect
from django.shortcuts import render
from django.template.loader import get_template
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
from .models import PluginList
from .models import Service
from .models import TcpCheck
from .tasks import http_check_task
from .tasks import ping_check_task
from .tasks import tcp_check_task


class MyView(View):
    def get(self, request):
        text = "Hello, World!"
        return HttpResponse(text)


@login_required
def home(request):
    services = Service.objects.filter(users=request.user).order_by("id")
    context = {"services": services}
    return render(request, "services.html", context)

@login_required
def service(request, pk):
    service_obj = Service.objects.get(id=pk)
    http_type = ContentType.objects.get_for_model(HttpCheck)
    http_checks_info = service_obj.checks.filter(content_type=http_type).order_by("id")

    ping_type = ContentType.objects.get_for_model(PingCheck)
    ping_checks_info = service_obj.checks.filter(content_type=ping_type).order_by("id")

    tcp_type = ContentType.objects.get_for_model(TcpCheck)
    tcp_checks_info = service_obj.checks.filter(content_type=tcp_type).order_by("id")

    context = {
        "service": service_obj,
        "http_checks": http_checks_info,
        "ping_checks": ping_checks_info,
        "tcp_checks": tcp_checks_info,
    }
    return render(request, "service_checks.html", context)

@login_required
def add_service(request):
    if not request.user.is_superuser:
        return redirect("checkerapp:home")

    if request.method == "POST":
        form = ServiceForm(request.POST)
        if form.is_valid():
            service_name = form.cleaned_data.get("name")
            selected_warning_plugins = request.POST.getlist("warning_listxblocks")
            selected_critical_plugins = request.POST.getlist("critical_listxblocks")
            service_obj = Service.objects.create(name=service_name)
            for plugin in selected_warning_plugins:
                service_obj.warning_severity.add(plugin)
            for plugin in selected_critical_plugins:
                service_obj.critical_severity.add(plugin)
            service_obj.users.add(request.user)
            messages.success(request, f" {service_name} created !!")
            return redirect("checkerapp:service", pk=service_obj.pk)

    form = ServiceForm()
    plugin_list = PluginList.objects.all()
    warning_plugins = []
    critical_plugins = []
    context = {
        "form": form,
        "plugin_list": plugin_list,
        "warning_plugins": warning_plugins,
        "critical_plugins": critical_plugins,
    }
    return render(request, "add_service.html", context)

@login_required
def edit_service(request, service_pk):
    if not request.user.is_superuser:
        return redirect("checkerapp:home")

    flag = True
    service_obj = Service.objects.get(id=service_pk)

    form = ServiceForm(request.POST or None, instance=service_obj)
    if form.is_valid():
        service_name = form.cleaned_data.get("name")
        selected_warning_plugins = request.POST.getlist("warning_listxblocks")
        selected_critical_plugins = request.POST.getlist("critical_listxblocks")
        for plugin in selected_warning_plugins:
            service_obj.warning_severity.add(plugin)
        for plugin in selected_critical_plugins:
            service_obj.critical_severity.add(plugin)

        service_obj = Service.objects.filter(id=service_pk).update(name=service_name)
        messages.success(request, f" {service_name} updated !!")
        return redirect("checkerapp:edit_service", service_pk=service_pk)

    plugin_list = PluginList.objects.all()
    warning_plugins = service_obj.warning_severity.all()
    critical_plugins = service_obj.critical_severity.all()
    context = {
        "form": form,
        "service": service_obj,
        "plugin_list": plugin_list,
        "warning_plugins": warning_plugins,
        "critical_plugins": critical_plugins,
        "flag": flag,
    }
    return render(request, "add_service.html", context)

@login_required
def delete_warning_plugin(request, service_pk, plugin_pk):
    service_obj = Service.objects.get(id=service_pk)
    plugin_obj = PluginList.objects.get(id=plugin_pk)
    service_obj.warning_severity.remove(plugin_obj)
    messages.success(request, f"{plugin_obj.name} removed from {service_obj.name} !")
    return redirect("checkerapp:edit_service", service_pk=service_pk)

@login_required
def delete_critical_plugin(request, service_pk, plugin_pk):
    service_obj = Service.objects.get(id=service_pk)
    plugin_obj = PluginList.objects.get(id=plugin_pk)
    service_obj.critical_severity.remove(plugin_obj)
    messages.success(request, f"{plugin_obj.name} removed from {service_obj.name} !")
    return redirect("checkerapp:edit_service", service_pk=service_pk)

@login_required
def delete_service(request, service_pk):
    service_obj = Service.objects.get(id=service_pk)
    base_checks = service_obj.checks.all()
    for checks in base_checks:
        checks.content_object.delete()
    service_obj.delete()
    messages.success(request, f" {service_obj.name} deleted !!")
    return redirect("checkerapp:home")

@login_required
def http_info(request, pk):
    http_results_obj = HttpCheck.objects.get(id=pk)
    base_check_obj = http_results_obj.base_check.first()
    result = http_results_obj.results.all().order_by("id")  # fetch status (UP/DOWN)
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
    }
    return render(request, "check_info/http_info.html", context)

@login_required
def ping_info(request, pk):
    ping_results_obj = PingCheck.objects.get(id=pk)
    base_check_obj = ping_results_obj.base_check.first()
    result = ping_results_obj.results.all().order_by("id")
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
        "last_down_time": last_down_time,
    }
    return render(request, "check_info/ping_info.html", context)

@login_required
def tcp_info(request, pk):
    tcp_results_obj = TcpCheck.objects.get(id=pk)
    base_check_obj = tcp_results_obj.base_check.first()
    result = tcp_results_obj.results.all().order_by("id")
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
        "last_down_time": last_down_time,
    }
    return render(request, "check_info/tcp_info.html", context)

@login_required
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
            severe_level = base_check_form.cleaned_data.get("severe_level")
            service_obj = Service.objects.get(id=service_pk)
            creator = User.objects.get(id=request.user.pk)
            http_base_check_obj = http_check.base_check.create(
                interval=interval,
                backoff_count=backoff_count,
                severe_level=severe_level,
                creator=creator,
            )
            service_obj.checks.add(http_base_check_obj)
            task_obj = {"base_check_obj": http_base_check_obj}
            http_check_task.apply_async(args=(task_obj,), queue="check_queue")
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

@login_required
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
        severe_level = base_check_form.cleaned_data.get("severe_level")
        BaseCheck.objects.filter(id=base_check_obj.id).update(
            interval=interval, backoff_count=backoff_count, severe_level=severe_level
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

@login_required
def add_ping_check(request, service_pk):
    if request.method == "POST":
        ping_check_form = PingCheckForm(request.POST)
        base_check_form = BaseCheckForm(request.POST)
        if ping_check_form.is_valid() and base_check_form.is_valid():
            ip_address = ping_check_form.cleaned_data.get("ip_address")
            ping_check = PingCheck.objects.create(ip_address=ip_address)
            interval = base_check_form.cleaned_data.get("interval")
            backoff_count = base_check_form.cleaned_data.get("backoff_count")
            severe_level = base_check_form.cleaned_data.get("severe_level")
            service_obj = Service.objects.get(id=service_pk)
            creator = User.objects.get(id=request.user.pk)
            ping_base_check_obj = ping_check.base_check.create(
                interval=interval,
                backoff_count=backoff_count,
                severe_level=severe_level,
                creator=creator,
            )
            service_obj.checks.add(ping_base_check_obj)
            task_obj = {"base_check_obj": ping_base_check_obj}
            ping_check_task.apply_async(args=(task_obj,), queue="check_queue")
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

@login_required
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
        severe_level = base_check_form.cleaned_data.get("severe_level")

        BaseCheck.objects.filter(id=base_check_obj.id).update(
            interval=interval, backoff_count=backoff_count, severe_level=severe_level
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

@login_required
def add_tcp_check(request, service_pk):
    if request.method == "POST":
        tcp_check_form = TcpCheckForm(request.POST)
        base_check_form = BaseCheckForm(request.POST)
        if tcp_check_form.is_valid() and base_check_form.is_valid():
            ip_address = tcp_check_form.cleaned_data.get("ip_address")
            tcp_check = TcpCheck.objects.create(ip_address=ip_address)
            interval = base_check_form.cleaned_data.get("interval")
            backoff_count = base_check_form.cleaned_data.get("backoff_count")
            severe_level = base_check_form.cleaned_data.get("severe_level")
            service_obj = Service.objects.get(id=service_pk)
            creator = User.objects.get(id=request.user.pk)
            tcp_base_check_obj = tcp_check.base_check.create(
                interval=interval,
                backoff_count=backoff_count,
                severe_level=severe_level,
                creator=creator,
            )
            service_obj.checks.add(tcp_base_check_obj)
            task_obj = {"base_check_obj": tcp_base_check_obj}
            tcp_check_task.apply_async(args=(task_obj,), queue="check_queue")
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

@login_required
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
        severe_level = base_check_form.cleaned_data.get("severe_level")
        BaseCheck.objects.filter(id=base_check_obj.id).update(
            interval=interval, backoff_count=backoff_count, severe_level=severe_level
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

@login_required
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

@login_required
def delete_check(request, service_type_id, service_pk, pk):
    selected_service_type = (
        BaseCheck.objects.filter(content_type_id=service_type_id).first().content_type
    )
    service_obj = BaseCheck.objects.get(
        object_id=pk, content_type=selected_service_type
    )
    service_obj.content_object.delete()

    return redirect("checkerapp:service", pk=service_pk)

@login_required
class RenderPDF:
    @staticmethod
    def render(path: str, params: dict):
        template = get_template(path)
        html = template.render(params)
        response = BytesIO()
        pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), response)
        if not pdf.err:
            return HttpResponse(response.getvalue(), content_type="application/pdf")

@login_required
class Pdf(View):
    def get(self, request, pk):

        base_check_obj = BaseCheck.objects.get(id=pk)
        last_down_time = (
            base_check_obj.content_object.results.filter(result=0)
            .order_by("-created_at")
            .first()
        )
        today = datetime.now()

        params = {
            "today": today,
            "base_check_obj": base_check_obj,
            "last_down_time": last_down_time,
            "result": base_check_obj.content_object.results.all(),
            "request": request,
        }
        return RenderPDF.render("pdf.html", params)
