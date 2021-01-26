from django.contrib.auth import views as auth_views
from django.urls import include
from django.urls import path

from accounts import views as accounts_views

app_name = "accounts"

urlpatterns = [
    path(
        "login", auth_views.LoginView.as_view(template_name="login.html"), name="login"
    ),
    path("logout", auth_views.LogoutView.as_view(), name="logout"),
    path("delete_user/<int:pk>", accounts_views.delete_user, name="delete_user"),
    path("users", accounts_views.user_list, name="user_list"),
    path("adduser", accounts_views.add_user, name="add_user"),
    path(
        "remove_user_service/<int:service_pk>/<int:user_pk>/",
        accounts_views.remove_user_service,
        name="remove_user_service",
    ),
    path(
        "service_users/<int:service_pk>/",
        accounts_views.service_users,
        name="service_users",
    ),
    path(
        "add_user_service/<int:service_pk>/",
        accounts_views.add_user_in_service,
        name="add_user_in_service",
    ),
    path("edit_user/<int:pk>/", accounts_views.edit_user, name="edit_user"),
    path("my_account", accounts_views.my_account, name="my_account"),
    path("change_password", accounts_views.change_password, name="change_password"),
    path("view_plugin/<str:plugin>", accounts_views.view_plugin, name="view_plugin"),
    path("plugin_list", accounts_views.plugin_list, name="plugin_list"),
    path(
        "plugin/generic_plugin",
        include("sc_generic_plugin.urls", namespace="generic_plugin"),
    ),
    path("plugin/telegram_plugin", include("bot.urls", namespace="telegram_plugin")),
]
