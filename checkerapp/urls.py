from django.urls import path

from checkerapp import views

# from checkerapp.views import Pdf

app_name = "checkerapp"

urlpatterns = [
    path("", views.home, name="home"),
    path("add_service", views.add_service, name="add_service"),
    path("service/<int:pk>/", views.service, name="service"),
    path("service/http_info/<int:pk>/", views.http_info, name="http_info"),
    path("service/ping_info/<int:pk>/", views.ping_info, name="ping_info"),
    path("service/tcp_info/<int:pk>/", views.tcp_info, name="tcp_info"),
    path(
        "service/<int:service_pk>/add_http_check/",
        views.add_http_check,
        name="add_http_check",
    ),
    path(
        "service/<int:service_pk>/add_ping_check/",
        views.add_ping_check,
        name="add_ping_check",
    ),
    path(
        "service/<int:service_pk>/add_tcp_check/",
        views.add_tcp_check,
        name="add_tcp_check",
    ),
    path(
        "service/<int:service_pk>/edit_http_check/<int:http_pk>/",
        views.edit_http_check,
        name="edit_http_check",
    ),
    path(
        "service/<int:service_pk>/edit_ping_check/<int:ping_pk>/",
        views.edit_ping_check,
        name="edit_ping_check",
    ),
    path(
        "service/<int:service_pk>/edit_tcp_check/<int:tcp_pk>/",
        views.edit_tcp_check,
        name="edit_tcp_check",
    ),
    path(
        "maintenance/<int:service_type_id>/<int:service_pk>/<int:pk>/",
        views.maintenance,
        name="maintenance",
    ),
    path(
        "delete_check/<int:service_type_id>/<int:service_pk>/<int:pk>/",
        views.delete_check,
        name="delete_check",
    ),
    # path("report/<int:pk>", Pdf.as_view(), name="report"),
    # path("maintenance/<int:pk>", views.maintenance, name="maintenance"),
    # path("edit_site/<int:pk>", views.edit_site, name="edit_site"),
    path("test", views.MyView.as_view(), name="test"),
]
