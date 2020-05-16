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
from .models import SiteList, User, Report
from .forms import UserForm, LoginForm, UserCreationForm
from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.decorators import login_required
from django_celery_results.models import TaskResult
from rest_framework.decorators import api_view
from rest_framework.response import Response

# Create your views here.
def home(request):
    sitenames = SiteList.objects.all()
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

	# pingreport = PingInfo.objects.get(id=pk)	
	result = TaskResult.objects.all()
	return render(request, 'ping_info.html', {'result' :result, 'user': User.objects.filter(is_staff=False) ,'site': SiteList.objects.get(id=pk)})

@login_required
def add_user(request):
	if request.method == "POST":
		form = UserForm(request.POST)
		if form.is_valid():
			# email = BaseUserManager.normalize_email(email)
			email = form.cleaned_data.get('email')
			username = form.cleaned_data.get('username')
			user = User.objects.create_user(email=email, username=username)
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
	sl = SiteList.objects.get(id=1)
	val = pingsite(sl.site_name)	
	# TaskResult.objects.create(site=sl.site_name)
	# TaskResult.save()
	if val==0:
		return sl.site_name + ' is Up'
	else:
		return 'Down'

app.conf.beat_schedule = {
    "ping-task": {
        "task": "checker.views.checksite",
        "schedule": crontab(hour="*", minute="*")
    }
}

