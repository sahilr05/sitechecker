from datetime import datetime
from io import BytesIO

import xhtml2pdf.pisa as pisa
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import EmptyPage
from django.core.paginator import PageNotAnInteger
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import redirect
from django.shortcuts import render
from django.template.loader import get_template
from django.views.generic import View

from .forms import *  # NOQA
from .models import *  # NOQA

# render to pdf


# Create your views here.
def home(request):
    if request.user.is_authenticated and not request.user.is_superuser:
        user = User.objects.get(id=request.user.id)
        site_names = user.sitelist_users.all()
        return render(request, "home.html", {"sitenames": site_names})

    site_names = SiteList.objects.all().order_by("id")
    return render(request, "home.html", {"sitenames": site_names})


def test(request):
    site_names = SiteList.objects.all().order_by("id")
    return render(request, "test.html", {"sitenames": site_names})


@login_required
def ping_info(request, pk):
    if request.method == "POST":
        selected_users = request.POST.getlist("listxblocks")
        # return HttpResponse(SelectedUsers)
        add_user_in_site = SiteList.objects.get(id=pk)
        for user in selected_users:
            add_user_in_site.users.add(User.objects.get(id=user))
            add_user_in_site.save()

    ping_report_obj = PingInfo.objects.filter(site_id=pk)
    site_list_obj = SiteList.objects.get(id=pk)
    user_list = site_list_obj.users.all()
    last_down_time = (
        ping_report_obj.filter(status="DOWN").order_by("-date_time").first()
    )

    # pagination
    page = request.GET.get("page", 1)
    paginator = Paginator(ping_report_obj, 10)
    try:
        ping_report = paginator.page(page)
    except PageNotAnInteger:
        ping_report = paginator.page(1)
    except EmptyPage:
        ping_report = paginator.page(paginator.num_pages)

    return render(
        request,
        "ping_info.html",
        {
            "result": ping_report,
            "add_users": User.objects.all(),
            "users": user_list,
            "site": site_list_obj,
            "last_down_time": last_down_time,
        },
    )


@login_required
def edit_site(request, pk):
    if not request.user.is_superuser:
        return redirect("checkerapp:home")
    site = SiteList.objects.get(id=pk)
    form = SiteForm(request.POST or None, instance=site)
    if form.is_valid():
        site_name = form.cleaned_data.get("site_name")
        interval = form.cleaned_data.get("interval")
        alert_type = form.cleaned_data.get("alert_type")
        failure_count = form.cleaned_data.get("failure_count")
        site = SiteList.objects.filter(id=pk).update(
            site_name=site_name,
            alert_type=alert_type,
            interval=interval,
            failure_count=failure_count,
            admin=User.objects.get(id=request.user.pk),
        )
        return redirect("checkerapp:home")
    return render(request, "edit_site.html", {"form": form})


@login_required
def add_site(request):
    if request.method == "POST":
        form = SiteForm(request.POST)
        if form.is_valid():
            site_name = form.cleaned_data.get("site_name")
            interval = form.cleaned_data.get("interval")
            failure_count = form.cleaned_data.get("failure_count")
            alert_type = form.cleaned_data.get("alert_type")
            site = SiteList.objects.create(
                site_name=site_name,
                alert_type=alert_type,
                interval=interval,
                failure_count=failure_count,
                admin=User.objects.get(id=request.user.pk),
            )
            site.save()
            return redirect("checkerapp:home")

    if not request.user.is_superuser:
        return redirect("checkerapp:home")
    form = SiteForm()
    return render(request, "add_site.html", context={"form": form})


@login_required
def delete_user(request, pk):
    user_to_delete = User.objects.get(id=pk)
    user_to_delete.delete()
    return redirect("user_list")


@login_required
def delete_site(request, pk):
    site_to_delete = SiteList.objects.get(id=pk)
    site_to_delete.delete()
    return redirect("checkerapp:home")


@login_required
def maintenance(request, pk):
    site = SiteList.objects.get(id=pk)
    maintenance_status = site.maintenance_mode
    if maintenance_status == 1:
        site.maintenance_mode = 0
    else:
        site.maintenance_mode = 1
    site.save()
    return redirect("checkerapp:home")


class Render_pdf:
    @staticmethod
    def render(path: str, params: dict):
        template = get_template(path)
        html = template.render(params)
        response = BytesIO()
        pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), response)
        if not pdf.err:
            return HttpResponse(response.getvalue(), content_type="application/pdf")
        else:
            return HttpResponse("Error Rendering PDF", status=400)


class Pdf(View):
    def get(self, request, pk):

        ping_report_obj = PingInfo.objects.filter(site_id=pk).order_by("-date_time")
        site_list_obj = SiteList.objects.get(id=pk)

        last_down_time = (
            ping_report_obj.filter(status="DOWN").order_by("-date_time").first()
        )
        today = datetime.now()

        params = {
            "today": today,
            "site_name": site_list_obj,
            "last_down_time": last_down_time,
            "result": ping_report_obj,
            "request": request,
        }
        return Render_pdf.render("pdf.html", params)
