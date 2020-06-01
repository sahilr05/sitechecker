from django.shortcuts import render, redirect, get_object_or_404
from datetime import timezone
from django.http import HttpResponse
import os
import schedule, datetime
from checker.tasks import pingsite
from sitechecker.celery import app
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from celery.task.schedules import crontab
from .models import *
from .forms import *
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view
from rest_framework.response import Response
from datetime import datetime
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

#render to pdf
from io import BytesIO
from django.template.loader import get_template
import xhtml2pdf.pisa as pisa
from django.views.generic import View


# Create your views here.
def home(request):
	if  request.user.is_authenticated and not request.user.is_superuser:	
		user = User.objects.get(id=request.user.id)
		site_names =  user.sitelist_users.all()
		return render(request, 'home.html', {'sitenames': site_names,})

	site_names = SiteList.objects.all().order_by('id')
	return render(request, 'home.html', {'sitenames': site_names,})

def test(request):
	site_names = SiteList.objects.all().order_by('id')
	return render(request, 'test.html', {'sitenames': site_names,})

@login_required
def ping_info(request, pk):
	if request.method == "POST":
		selected_users = request.POST.getlist('listxblocks')
		# return HttpResponse(SelectedUsers)
		add_user_in_site = SiteList.objects.get(id=pk)
		for user in selected_users:
			add_user_in_site.users.add(User.objects.get(id=user))
			add_user_in_site.save()

	ping_report_obj = PingInfo.objects.filter(site_id=pk)	
	site_list_obj = SiteList.objects.get(id=pk)
	user_list = site_list_obj.users.all()
	last_down_time = ping_report_obj.filter(status='DOWN').order_by('-date_time').first()

	#pagination 
	page = request.GET.get('page', 1)
	paginator = Paginator(ping_report_obj, 5)
	try:
		ping_report = paginator.page(page)
	except PageNotAnInteger:
		ping_report = paginator.page(1)
	except EmptyPage:
		ping_report = paginator.page(paginator.num_pages)

	return render(request, 'ping_info.html', {'result' :ping_report, 
				'add_users': User.objects.all(),
				'users': user_list,
				'site': site_list_obj,
				'last_down_time': last_down_time,
				})

@login_required
def remove_user(request, site_pk, user_pk):
	user_to_remove = User.objects.get(id=user_pk)
	site = SiteList.objects.get(id=site_pk)
	site.users.remove(user_to_remove)
	site.save()
	return redirect('ping_info', pk=site_pk)


@login_required
def edit_site(request, pk):
	if not request.user.is_superuser:
		return redirect('home')
	site = SiteList.objects.get(id=pk)
	form = SiteForm(request.POST or None, instance=site)
	if form.is_valid():
		site_name = form.cleaned_data.get('site_name')
		interval = form.cleaned_data.get('interval')
		alert_type= form.cleaned_data.get('alert_type')
		failure_count = form.cleaned_data.get('failure_count')
		site = SiteList.objects.filter(id=pk).update(site_name=site_name, alert_type=alert_type, interval=interval, failure_count = failure_count, admin=User.objects.get(id=request.user.pk))
		return redirect('home')
	return render(request, "edit_site.html", {'form':form})	

@login_required
def edit_user(request, pk):
	if not request.user.is_superuser:
		return redirect('home')
	user_info = User.objects.get(id=pk)
	form = EditUserForm(request.POST or None, instance=user_info)
	if form.is_valid():
		email = form.cleaned_data.get('email')
		username = form.cleaned_data.get('username')
		user = User.objects.filter(id=pk).update(email=email, username=username)
		return redirect('user_list')
	return render(request, "edit_user.html", {'form':form})	
	
@login_required
def user_list(request):
	if not request.user.is_superuser:
		return redirect('home')
	list_of_users = User.objects.filter(is_superuser=False)
	return render(request,
				  "user_list.html",
				  context={"users":list_of_users})


@login_required
def add_user(request):
	if request.method == "POST":
		form = UserForm(request.POST)
		if form.is_valid():
			email = form.cleaned_data.get('email')
			username = form.cleaned_data.get('username')
			password = form.cleaned_data.get('password')
			user = User.objects.create_user(email=email, username=username, password=password)
			user.save()
			return redirect("user_list")

	# if not request.user.is_superuser:
	# 	return redirect('home')
	form = UserForm()
	return render(request,
				  "add_user.html",
				  context={"form":form})

@login_required
def add_site(request):
	if request.method == "POST":
		form = SiteForm(request.POST)
		if form.is_valid():
			site_name = form.cleaned_data.get('site_name')
			interval = form.cleaned_data.get('interval')
			failure_count = form.cleaned_data.get('failure_count')
			alert_type = form.cleaned_data.get('alert_type')
			site = SiteList.objects.create(site_name=site_name, alert_type=alert_type, interval=interval, failure_count = failure_count, admin=User.objects.get(id=request.user.pk))
			site.save()
			return redirect("home")
		
	if not request.user.is_superuser:
		return redirect('home')	
	form = SiteForm()
	return render(request,
				  "add_site.html",
				  context={"form":form})

@login_required
def delete_user(request, pk):
	user_to_delete = User.objects.get(id=pk)
	user_to_delete.delete()
	return redirect('user_list')

@login_required
def delete_site(request, pk):
	site_to_delete = SiteList.objects.get(id=pk)
	site_to_delete.delete()
	return redirect('home')

@login_required
def maintenance(request, pk):
	site = SiteList.objects.get(id=pk)
	maintenance_status = site.maintenance_mode
	if maintenance_status == 1:
		site.maintenance_mode = 0
	else:
		site.maintenance_mode = 1
	site.save()
	return redirect('home')

@login_required
def logout_request(request):
	logout(request)
	return redirect("home")

def login_request(request):
	if request.method == "POST":
		form = LoginForm(request.POST)
		if form.is_valid():
			username = form.cleaned_data.get('username')
			password = form.cleaned_data.get('password')
			user = authenticate(username=username, password=password)
			if user is not None:
				login(request, user)
				messages.info(request, f"You are now logged in as {username}")
				return redirect("home")
			else:
				messages.error(request, "Invalid username or password")
		else:
			messages.error(request, "Invalid Credentials")

	form = LoginForm()
	return render(request,
				  "login.html",
				  {"form":form})


class Render_pdf:

    @staticmethod
    def render(path: str, params: dict):
        template = get_template(path)
        html = template.render(params)
        response = BytesIO()
        pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), response)
        if not pdf.err:
            return HttpResponse(response.getvalue(), content_type='application/pdf')
        else:
            return HttpResponse("Error Rendering PDF", status=400)

class Pdf(View):

	def get(self, request, pk):

		ping_report_obj = PingInfo.objects.filter(site_id=pk).order_by('-date_time')
		site_list_obj = SiteList.objects.get(id=pk)

		last_down_time = ping_report_obj.filter(status='DOWN').order_by('-date_time').first()
		today = datetime.now()

		params = {
			'today': today,
			'site_name' : site_list_obj,
			'last_down_time' : last_down_time,
			'result': ping_report_obj,
			'request': request
		}
		return Render_pdf.render('pdf.html', params)

			# email = BaseUserManager.normalize_email(email)
			
	# ExcludeUsers = SiteListObj.users.filter('username')
	# AddUsers = User.objects.exclude(ExcludeUsers)
	# pl = PingInfo.objects.filter(site_id=2)
	# last_down_time = pingreport.order_by('-date_time').filter(status='DOWN').values('date_time').first()

# @app.task
# def checksite(request=True):
# 	sl = SiteList.objects.values_list('site_name', flat=True)
# 	for site in sl:
# 		val = pingsite(site)
# 		if val==0:
# 			op = 'UP'
# 		else:
# 			op = 'DOWN'
# 		select_id = SiteList.objects.filter(site_name=site).values('id')
# 		new_info = PingInfo.objects.create(status=op,site_id=select_id)
# 		new_info.save()

# app.conf.beat_schedule = {
#     "ping-task": {
#         "task": "checker.views.checksite",
#         "schedule": crontab(minute="*", hour="*", day_of_week='*')
#     }
# }

# backup
# def checksite(request=True):
# 	sl = SiteList.objects.values_list('site_name', flat=True)
# 	for site in sl:
# 		val = pingsite(site)
# 		if val==0:
# 			op = 'UP'
# 		else:
# 			op = 'DOWN'
# 		select_id = SiteList.objects.filter(site_name=site).values('id')
# 		new_info = PingInfo.objects.create(status=op,site_id=select_id)
# 		new_info.save()
