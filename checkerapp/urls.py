from django.urls import path

from checkerapp import views
from checkerapp.views import Pdf

app_name = "checkerapp"

urlpatterns = [
    path("", views.home, name="home"),
    path("ping/<int:pk>/", views.ping_info, name="ping_info"),
    path("add_site", views.add_site, name="add_site"),
    path("report/<int:pk>", Pdf.as_view(), name="report"),
    path("maintenance/<int:pk>", views.maintenance, name="maintenance"),
    path("edit_site/<int:pk>", views.edit_site, name="edit_site"),
    path("delete_site/<int:pk>", views.delete_site, name="delete_site"),
]
