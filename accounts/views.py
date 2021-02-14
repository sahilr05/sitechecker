from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from django.shortcuts import redirect
from django.shortcuts import render

from .forms import EditUserForm
from .forms import MyAccountForm
from .forms import UserForm
from checkerapp.models import AlertPlugin
from checkerapp.models import Service


@login_required
def delete_user(request, pk):
    user_to_delete = User.objects.get(id=pk)
    user_to_delete.delete()
    messages.success(request, f" {user_to_delete.username} deleted from user list !!")
    return redirect("accounts:user_list")


@login_required
def edit_user(request, pk):
    if not request.user.is_superuser:
        return redirect("checkerapp:home")
    user_info = User.objects.get(id=pk)

    form = EditUserForm(request.POST or None, instance=user_info)
    if form.is_valid():
        form.save()
        messages.success(request, f"Account info updated ! !")
        return redirect("accounts:user_list")

    context = {"form": form}
    return render(request, "edit_user.html", context)


@login_required
def user_list(request):
    if not request.user.is_superuser:
        return redirect("checkerapp:home")
    list_of_users = User.objects.filter(is_superuser=False).order_by("id")
    return render(request, "user_list.html", context={"users": list_of_users})


@login_required
def add_user(request):
    if request.method == "POST":
        user_form = UserForm(request.POST)
        if user_form.is_valid():
            email = user_form.cleaned_data.get("email")
            username = user_form.cleaned_data.get("username")
            password = user_form.cleaned_data.get("password")
            user = User.objects.create_user(
                email=email, username=username, password=password
            )
            user.save()
            messages.success(request, f"{user.username} added to users list !")
            return redirect("accounts:user_list")

    context = {"form": UserForm()}
    return render(request, "add_user.html", context)

@login_required
def add_user_in_service(request, service_pk):
    selected_users = request.POST.getlist("listxblocks")
    service_obj = Service.objects.get(id=service_pk)
    for user in selected_users:
        service_obj.users.add(user)
    return redirect("accounts:service_users", service_pk=service_pk)

@login_required
def remove_user_service(request, service_pk, user_pk):
    user = User.objects.get(id=user_pk)
    service_obj = Service.objects.get(id=service_pk)
    service_obj.users.remove(user)
    messages.success(request, f"{user.username} removed from {service_obj.name} !")
    return redirect("accounts:service_users", service_pk=service_pk)

@login_required
def service_users(request, service_pk):
    service_obj = Service.objects.get(id=service_pk)
    service_users = service_obj.users.all()
    all_users = User.objects.all()
    context = {"users": service_users, "all_users": all_users, "service": service_obj}
    return render(request, "service_users.html", context)

@login_required
def my_account(request):
    user_info = User.objects.get(id=request.user.pk)
    if user_info:
        form = MyAccountForm(request.POST or None, instance=user_info)
    else:
        form = MyAccountForm()
    if form.is_valid():
        form.save()
        messages.success(request, f"Account info updated ! !")
        return redirect("accounts:my_account")

    context = {"form": form}
    return render(request, "my_account.html", context)

@login_required
def change_password(request):
    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, f"Password Changed !")
            return redirect("checkerapp:home")
        else:
            for msg in form.error_messages:
                messages.error(request, f"{msg}: {form.error_messages[msg]}")

    context = {"form": PasswordChangeForm(request.user)}
    return render(request, "change_pass.html", context)

@login_required
def plugin_list(request):
    plugins_name = [cls.__name__ for cls in AlertPlugin.__subclasses__()]
    plugins_obj = [cls for cls in AlertPlugin.__subclasses__()]

    context = {}
    context["plugin_data"] = zip(plugins_name, plugins_obj)
    return render(request, "plugins/plugin_list.html", context)

@login_required
def view_plugin(request, plugin):
    plugin_obj = plugin()
    return redirect(plugin_obj.url)
