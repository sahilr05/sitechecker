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
from .models import SiteList, PingInfo, User
from .forms import UserForm, LoginForm, UserCreationForm
from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.decorators import login_required

# Create your views here.
def home(request):
    sitenames = SiteList.objects.all()
    return render(request, 'home.html', {'sitenames': sitenames})

@login_required
def info(request, pk):
	pingreport = PingInfo.objects.get(id=pk)	
	return render(request, 'ping_info.html', {'pingreport': pingreport, 'user': User.objects.filter(is_staff=False) ,'site': SiteList.objects.get(id=pk)})

# def signup(request):
# 	if request.method == "POST":
# 		form = UserForm(request.POST)
# 		if form.is_valid():
# 			username = form.cleaned_data.get('username')
# 			password = form.cleaned_data.get('password')
# 			confpass = form.cleaned_data.get('confirm_password')
# 			if confpass != password:
# 				messages.error(request, "Passwords don't match")
# 			user = User.objects.create_user(username=username,password=password)
# 			user.save()
# 			user = authenticate(username=username,password=password)
# 			if user is not None:
# 				login(request, user)
# 			else:
# 				messages.error(request, 'Invalid Credentials')
# 			return redirect("checker:home")
# 		else:
# 			for msg in form.error_messages:
# 				messages.error(request, f"{msg}: {form.error_messages[msg]}")

# 	form = UserForm()
# 	return render(request,
# 				  "signup.html",
# 				  context={"form":form})

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
		else:
			for msg in form.error_messages:				
				messages.error(request, f"{msg}: {form.error_messages[msg]}")

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
    val = pingsite('google.com')
    if val==0:
        return 'Up'
    else:
        return 'Down'

app.conf.beat_schedule = {
    "ping-task": {
        "task": "checker.views.checksite",
        "schedule": crontab(hour="*", minute="*")
    }
}

