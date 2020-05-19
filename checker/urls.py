from django.urls import path, include
from checker import views

# app_name = 'checker'

urlpatterns = [
    path('',views.home, name='home'),
    path('ping/<int:pk>/',views.info, name= 'info'),
    path('users',views.user_list, name='user_list'),
    path('adduser',views.add_user, name = 'add_user'),
    path('login/',views.login_request, name= 'login'),
    path('logout',views.logout_request, name= 'logout'),
    path('add_site',views.add_site, name='add_site'),
]


    # path('checksite',views.checksite, name='checksite'),
    # path('ping/<int:pk>/',views.info, name = 'info'),
    # path('api/test', views.test, name='api_test'),
    # path('signup',views.signup, name = 'signup'),