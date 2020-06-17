# from datetime import datetime
# from io import BytesIO
# import xhtml2pdf.pisa as pisa
# from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import redirect
from django.shortcuts import render
from django.views import View

from .forms import BaseCheckForm
from .forms import HttpCheckForm
from .forms import PingCheckForm
from .models import BaseCheck
from .models import ContentType
from .models import HttpCheck
from .models import PingCheck
from .models import Service
from .models import TcpCheck

# from .forms import TcpCheckForm

# from django.core.paginator import EmptyPage
# from django.core.paginator import PageNotAnInteger
# from django.core.paginator import Paginator
# from django.views.generic import View
# from .models import BaseCheck
# from django.template.loader import get_template


class MyView(View):
    def get(self, request):
        text = "Hello, World!"
        return HttpResponse(text)


# class TestView(MyView):
#     def get(self, request):
#         return HttpResponse(self.text)


def test(request):
    return HttpResponse("Testing")


def home(request):
    services = Service.objects.all().order_by("id")
    context = {"services": services}
    return render(request, "services.html", context)


def service(request, pk):
    service_obj = Service.objects.get(id=pk)
    # service_checks = service_obj.checks.all()
    http_type = ContentType.objects.get_for_model(HttpCheck)
    http_checks_info = service_obj.checks.filter(content_type=http_type)

    ping_type = ContentType.objects.get_for_model(PingCheck)
    ping_checks_info = service_obj.checks.filter(content_type=ping_type)

    tcp_type = ContentType.objects.get_for_model(TcpCheck)
    tcp_checks_info = service_obj.checks.filter(content_type=tcp_type)

    # service_models = [HttpCheck, PingCheck, TcpCheck]
    context = {
        "service": service_obj,
        "http_checks": http_checks_info,
        "ping_checks": ping_checks_info,
        "tcp_checks": tcp_checks_info,
    }
    return render(request, "service_info.html", context)


def http_info(request, pk):
    http_check_obj = HttpCheck.objects.get(id=pk)  # fetch site name from HttpCheck
    base_check_obj = (
        http_check_obj.base_check.first()
    )  # fetch interval, backoff count, etc.
    result = http_check_obj.results.all()  # fetch status (UP/DOWN)

    context = {"result": result, "site": http_check_obj, "base_check": base_check_obj}
    return render(request, "ping_info.html", context)


def ping_info(request, pk):
    ping_results_obj = PingCheck.objects.get(id=pk)
    base_check_obj = ping_results_obj.base_check.first()
    result = ping_results_obj.results.all()

    context = {
        "result": result,
        "ip_address": ping_results_obj,
        "base_check": base_check_obj,
    }
    return render(request, "ping_info.html", context)


def tcp_info(request, pk):
    tcp_results_obj = TcpCheck.objects.get(id=pk)
    base_check_obj = tcp_results_obj.base_check.first()
    result = tcp_results_obj.results.all()

    context = {
        "result": result,
        "ip_address": tcp_results_obj,
        "base_check": base_check_obj,
    }
    return render(request, "tcp_info.html", context)


def add_http_check(request, service_pk):
    if request.method == "POST":
        http_check_form = HttpCheckForm(request.POST)
        base_check_form = BaseCheckForm(request.POST)
        if http_check_form.is_valid() and base_check_form.is_valid():
            site_name = http_check_form.cleaned_data.get("site_name")
            expected_status_code = http_check_form.cleaned_data.get(
                "expected_status_code"
            )
            httpcheck = HttpCheck.objects.create(
                site_name=site_name, expected_status_code=expected_status_code
            )
            interval = base_check_form.cleaned_data.get("interval")
            backoff_count = base_check_form.cleaned_data.get("backoff_count")
            alert_type = base_check_form.cleaned_data.get("alert_type")
            severe_level = base_check_form.cleaned_data.get("severe_level")
            service_obj = Service.objects.get(id=service_pk)
            http_base_check_obj = httpcheck.base_check.create(
                interval=interval,
                backoff_count=backoff_count,
                alert_type=alert_type,
                severe_level=severe_level,
                creator=User.objects.get(id=request.user.pk),
            )
            service_obj.checks.add(http_base_check_obj)
            return redirect("checkerapp:service", pk=service_pk)

    if not request.user.is_superuser:
        return redirect("checkerapp:service", pk=service_pk)
    http_check_form = HttpCheckForm()
    base_check_form = BaseCheckForm()
    context = {"http_check_form": http_check_form, "base_check_form": base_check_form}
    return render(request, "add_http_check.html", context)


def edit_http_check(request, service_pk, http_pk):
    http_check_obj = HttpCheck.objects.get(id=http_pk)
    base_check_obj = http_check_obj.base_check.first()
    http_check_form = HttpCheckForm(request.POST)
    base_check_form = BaseCheckForm(request.POST)
    if http_check_form.is_valid() and base_check_form.is_valid():
        site_name = http_check_form.cleaned_data.get("site_name")
        expected_status_code = http_check_form.cleaned_data.get("expected_status_code")
        httpcheck = HttpCheck.objects.create(
            site_name=site_name, expected_status_code=expected_status_code
        )
        interval = base_check_form.cleaned_data.get("interval")
        backoff_count = base_check_form.cleaned_data.get("backoff_count")
        alert_type = base_check_form.cleaned_data.get("alert_type")
        severe_level = base_check_form.cleaned_data.get("severe_level")
        service_obj = Service.objects.get(id=service_pk)
        http_base_check_obj = httpcheck.base_check.create(
            interval=interval,
            backoff_count=backoff_count,
            alert_type=alert_type,
            severe_level=severe_level,
            creator=User.objects.get(id=request.user.pk),
        )
        service_obj.checks.add(http_base_check_obj)
        return redirect("checkerapp:service", pk=service_pk)

    http_check_form = HttpCheckForm(request.POST or None, instance=http_check_obj)
    base_check_form = BaseCheckForm(request.POST or None, instance=base_check_obj)
    context = {"http_check_form": http_check_form, "base_check_form": base_check_form}
    return render(request, "add_http_check.html", context)


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
            ping_base_check_obj = ping_check.base_check.create(
                interval=interval,
                backoff_count=backoff_count,
                alert_type=alert_type,
                severe_level=severe_level,
                creator=User.objects.get(id=request.user.pk),
            )
            service_obj.checks.add(ping_base_check_obj)
            return redirect("checkerapp:service", pk=service_pk)

    if not request.user.is_superuser:
        return redirect("checkerapp:service", pk=service_pk)
    ping_check_form = PingCheckForm()
    base_check_form = BaseCheckForm()
    context = {"ping_check_form": ping_check_form, "base_check_form": base_check_form}
    return render(request, "add_ping_check.html", context)


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
