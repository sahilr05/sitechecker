"""sitechecker URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, include
from checker import views

# app_name = 'checker'

urlpatterns = [
    # path('checksite',views.checksite, name='checksite'),
    path('',views.home, name='home'),
    # path('ping/<int:pk>/',views.info, name = 'info'),
    path('ping/<int:pk>/',views.info, name= 'info'),
    path('adduser',views.add_user, name = 'add_user'),
    # path('signup',views.signup, name = 'signup'),
    path('login/',views.login_request, name= 'login'),
    path('logout',views.logout_request, name= 'logout'),
]
