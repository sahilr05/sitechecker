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
    path(
        "add_user_in_check/<int:base_check_pk>/<int:check_pk>/",
        accounts_views.add_user_check,
        name="add_user_in_check",
    ),
    path("users", accounts_views.user_list, name="user_list"),
    path("adduser", accounts_views.add_user, name="add_user"),
    path(
        "remove_user/<int:base_check_pk>/<int:site_pk>/<int:user_pk>",
        accounts_views.remove_user,
        name="remove_user",
    ),
    path("edit_user/<int:pk>/", accounts_views.edit_user, name="edit_user"),
    path("my_account", accounts_views.my_account, name="my_account"),
    path("change_password", accounts_views.change_password, name="change_password"),
    # path(
    #     "plugin/telegram_old", accounts_views.telegram_plugin, name="telegram_plugin"
    # ),
    path("view_plugin/<str:plugin>", accounts_views.view_plugin, name="view_plugin"),
    path("plugin_list", accounts_views.plugin_list, name="plugin_list"),
    path("plugin/sms_plugin", accounts_views.sms_plugin, name="sms_plugin"),
    path("plugin/email_plugin", accounts_views.email_plugin, name="email_plugin"),
    path(
        "plugin/telegram_plugin",
        include("sc_telegram_plugin.urls", namespace="telegram_plugin"),
    ),
]
