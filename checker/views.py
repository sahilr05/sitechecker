from django.shortcuts import render, redirect
from django.http import HttpResponse
import os
import schedule, datetime
from checker.tasks import pingsite
from sitechecker.celery import app
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from celery.task.schedules import crontab
from .models import SiteList, User, PingInfo
from .forms import UserForm, LoginForm, UserCreationForm, SiteForm
# from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.decorators import login_required
# from django_celery_results.models import TaskResult
from rest_framework.decorators import api_view
from rest_framework.response import Response
# from .redis_utils import RedisManager
from datetime import datetime

# Create your views here.
def home(request):
	site_names = SiteList.objects.all().order_by('id')
	return render(request, 'home.html', {'sitenames': site_names,})

@login_required
def info(request, pk):
	if request.method == "POST":
		selected_users = request.POST.getlist('listxblocks')
		# return HttpResponse(SelectedUsers)
		add_user_in_site = SiteList.objects.get(id=pk)
		for user in selected_users:
			add_user_in_site.users.add(User.objects.get(id=user))
			add_user_in_site.save()

	ping_report = PingInfo.objects.filter(site_id=pk)	
	site_list_obj = SiteList.objects.get(id=pk)
	user_list = site_list_obj.users.all()

	last_down_time = ping_report.filter(status='DOWN').order_by('-date_time').first()

	return render(request, 'ping_info.html', {'result' :ping_report, 
				'add_users': User.objects.all(),
				'users': user_list,
				'site': SiteList.objects.get(id=pk),
				'last_down_time': last_down_time,
				})

@login_required
def user_list(request):
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
			return redirect("home")

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
			interval_temp = form.cleaned_data.get('interval')
			interval = ' '.join(list(interval_temp))
			failure_count = form.cleaned_data.get('number_of_failure')
			site = SiteList.objects.create(site_name=site_name, interval=interval, failure_count = failure_count, admin=User.objects.get(id=request.user.pk))
			site.save()
			return redirect("home")
		
	form = SiteForm()
	return render(request,
				  "add_site.html",
				  context={"form":form})

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
