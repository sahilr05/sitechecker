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
from .forms import UserForm, LoginForm, UserCreationForm
# from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.decorators import login_required
# from django_celery_results.models import TaskResult
from rest_framework.decorators import api_view
from rest_framework.response import Response
# from .redis_utils import RedisManager
from datetime import datetime

# Create your views here.
def home(request):
    sitenames = SiteList.objects.all().order_by('id')
    return render(request, 'home.html', {'sitenames': sitenames})

@login_required
def info(request, pk):
	if request.method == "POST":
		SelectedUsers = request.POST.getlist('listxblocks')
		# return HttpResponse(SelectedUsers)
		rel = SiteList.objects.get(id=pk)
		for s in SelectedUsers:
			rel.users.add(User.objects.get(id=s))
			rel.save()

	pingreport = PingInfo.objects.filter(site_id=pk)	
	sl = SiteList.objects.get(id=pk)
	user = sl.users.all()
	# user = SiteList.objects.filter(sitelist_users=2)	
	# user = SiteList.sitelist_users.objects.filter(sitelist_id=pk)
	# result = TaskResult.objects.all()
	# r = RedisManager('google.com 20 : 05 : 17 : 13*')
	# google.com 20 : 05 : 17 : 13*
	# op = r.get_multiple('status', 'date')
	# return HttpResponse(op)
	# result = 
	return render(request, 'ping_info.html', {'result' :pingreport, 'add_users': User.objects.all() ,'users': user ,'site': SiteList.objects.get(id=pk)})

@login_required
def add_user(request):
	if request.method == "POST":
		form = UserForm(request.POST)
		if form.is_valid():
			# email = BaseUserManager.normalize_email(email)
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

@app.task
def checksite(request=True):
	sl = SiteList.objects.values_list('site_name', flat=True)
	for site in sl:
		val = pingsite(site)
		if val==0:
			op = 'UP'
		else:
			op = 'DOWN'
		select_id = SiteList.objects.filter(site_name=site).values('id')
		new_info = PingInfo.objects.create(status=op,site_id=select_id)
		new_info.save()
	
	# name = sl.site_name 
	# val = pingsite(name)
	# if val==0:
	# 	op = 'UP'
	# else:
	# 	op = 'DOWN'

app.conf.beat_schedule = {
    "ping-task": {
        "task": "checker.views.checksite",
        "schedule": crontab(hour="*", minute="*")
    }
}
# sites = SiteList.objects.all()
# for site in sites:
#     if site.need_to_be_checked():
#         another_task.apply_async(args=[site.name], queue="foobar")


	# dt = datetime.now().strftime('%H:%M:%S')
	# day = datetime.now().strftime('%y : %m : %d : %H : %M : %S')
	# strftime('%y : %m : %H : %M : %S')

	# r = RedisManager(name + ' ' + day)
	# data = {'status':op,'date':dt}
	# r.set_multiple(data)
	# r.set_value(op)
