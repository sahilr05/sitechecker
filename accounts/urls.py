from django.urls import path

from accounts import views as accounts_views

app_name = "accounts"

urlpatterns = [
    path("login/", accounts_views.login_request, name="login"),
    path("logout", accounts_views.logout_request, name="logout"),
    path("delete_user/<int:pk>", accounts_views.delete_user, name="delete_user"),
    path("users", accounts_views.user_list, name="user_list"),
    path("adduser", accounts_views.add_user, name="add_user"),
    path(
        "remove_user/<int:site_pk>/<int:user_pk>",
        accounts_views.remove_user,
        name="remove_user",
    ),
    path("edit_user/<int:pk>", accounts_views.edit_user, name="edit_user"),
]
