from django.urls import include
from django.urls import path

from checkerapp import views
from checkerapp.views import Pdf

# app_name = 'checkerapp'

urlpatterns = [
    path("", views.home, name="home"),
    path("ping/<int:pk>/", views.ping_info, name="ping_info"),
    path("users", views.user_list, name="user_list"),
    path("adduser", views.add_user, name="add_user"),
    path("login/", views.login_request, name="login"),
    path("logout", views.logout_request, name="logout"),
    path("add_site", views.add_site, name="add_site"),
    path("report/<int:pk>", Pdf.as_view(), name="report"),
    path("maintenance/<int:pk>", views.maintenance, name="maintenance"),
    path(
        "remove_user/<int:site_pk>/<int:user_pk>", views.remove_user, name="remove_user"
    ),
    path("edit_site/<int:pk>", views.edit_site, name="edit_site"),
    path("edit_user/<int:pk>", views.edit_user, name="edit_user"),
    path("delete_site/<int:pk>", views.delete_site, name="delete_site"),
    path("delete_user/<int:pk>", views.delete_user, name="delete_user"),
]
