from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import redirect
from django.shortcuts import render

from checkerapp.forms import EditUserForm
from checkerapp.forms import UserForm
from checkerapp.models import SiteList


def test(request):
    return HttpResponse("Hi")


@login_required
def delete_user(request, pk):
    user_to_delete = User.objects.get(id=pk)
    user_to_delete.delete()
    return redirect("accounts:user_list")


@login_required
def remove_user(request, site_pk, user_pk):
    user_to_remove = User.objects.get(id=user_pk)
    site = SiteList.objects.get(id=site_pk)
    site.users.remove(user_to_remove)
    site.save()
    return redirect("checkerapp:ping_info", pk=site_pk)


@login_required
def edit_user(request, pk):
    if not request.user.is_superuser:
        return redirect("checkerapp:home")
    user_info = User.objects.get(id=pk)
    form = EditUserForm(request.POST or None, instance=user_info)
    if form.is_valid():
        email = form.cleaned_data.get("email")
        username = form.cleaned_data.get("username")
        user = User.objects.filter(id=pk).update(email=email, username=username)  # NOQA
        return redirect("accounts:user_list")
    return render(request, "edit_user.html", {"form": form})


@login_required
def user_list(request):
    if not request.user.is_superuser:
        return redirect("checkerapp:home")
    list_of_users = User.objects.filter(is_superuser=False)
    return render(request, "user_list.html", context={"users": list_of_users})


@login_required
def add_user(request):
    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get("email")
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = User.objects.create_user(
                email=email, username=username, password=password
            )
            user.save()
            return redirect("accounts:user_list")

    form = UserForm()
    return render(request, "add_user.html", context={"form": form})