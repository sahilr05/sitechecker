from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse
from django.shortcuts import redirect
from django.shortcuts import render

from checkerapp.forms import EditUserForm
from checkerapp.forms import ProfileForm
from checkerapp.forms import UserForm
from checkerapp.models import BaseCheck
from checkerapp.models import HttpCheck
from checkerapp.models import PingCheck
from checkerapp.models import TcpCheck


def test(request):
    return HttpResponse("Hi")


@login_required
def delete_user(request, pk):
    user_to_delete = User.objects.get(id=pk)
    user_to_delete.delete()
    return redirect("accounts:user_list")


@login_required
def remove_user(request, base_check_pk, site_pk, user_pk):
    user_to_remove = User.objects.get(id=user_pk)
    base_check_obj = BaseCheck.objects.get(id=base_check_pk)
    base_check_obj.users.remove(user_to_remove)
    base_check_obj.save()

    http_type = ContentType.objects.get_for_model(HttpCheck)
    ping_type = ContentType.objects.get_for_model(PingCheck)
    tcp_type = ContentType.objects.get_for_model(TcpCheck)

    if base_check_obj.content_type == http_type:
        check = "checkerapp:http_info"
    elif base_check_obj.content_type == ping_type:
        check = "checkerapp:ping_info"
    elif base_check_obj.content_type == tcp_type:
        check = "checkerapp:tcp_info"
    else:
        return HttpResponse("invalid request")

    return redirect(check, pk=site_pk)


@login_required
def edit_user(request, pk):
    if not request.user.is_superuser:
        return redirect("checkerapp:home")
    user_info = User.objects.get(id=pk)

    if user_info.profile:
        profile_form = ProfileForm(request.POST or None, instance=user_info.profile)
    else:
        profile_form = ProfileForm()

    form = EditUserForm(request.POST or None, instance=user_info)
    # profile_form = ProfileForm(request.POST or None, instance=user_info.profile)
    if form.is_valid() and profile_form.is_valid():
        form.save()
        profile_form.save()
        return redirect("accounts:user_list")

    context = {"form": form, "profile_form": profile_form}
    return render(request, "edit_user.html", context)


def add_user_check(request, base_check_pk, check_pk):
    selected_users = request.POST.getlist("listxblocks")
    base_check_obj = BaseCheck.objects.get(id=base_check_pk)
    for user in selected_users:
        base_check_obj.users.add(user)
    http_type = ContentType.objects.get_for_model(HttpCheck)
    ping_type = ContentType.objects.get_for_model(PingCheck)
    tcp_type = ContentType.objects.get_for_model(TcpCheck)

    if base_check_obj.content_type == http_type:
        check = "checkerapp:http_info"
    elif base_check_obj.content_type == ping_type:
        check = "checkerapp:ping_info"
    elif base_check_obj.content_type == tcp_type:
        check = "checkerapp:tcp_info"
    else:
        return HttpResponse("invalid request")
    return redirect(check, pk=check_pk)
    # context={"":}


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
        profile_form = ProfileForm(request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            phone = profile_form.cleaned_data.get("phone")
            email = user_form.cleaned_data.get("email")
            username = user_form.cleaned_data.get("username")
            password = user_form.cleaned_data.get("password")
            user = User.objects.create_user(
                email=email, username=username, password=password
            )
            user.profile.phone = phone
            user.save()
            return redirect("accounts:user_list")

    context = {"form": UserForm(), "profile_form": ProfileForm()}
    return render(request, "add_user.html", context)


def my_account(request):
    if not request.user.is_superuser:
        return redirect("checkerapp:home")
    user_info = User.objects.get(id=request.user.pk)

    if user_info.profile:
        profile_form = ProfileForm(request.POST or None, instance=user_info.profile)
    else:
        profile_form = ProfileForm()

    form = EditUserForm(request.POST or None, instance=user_info)
    if form.is_valid() and profile_form.is_valid():
        form.save()
        profile_form.save()
        return redirect("checkerapp:home")

    context = {"form": form, "profile_form": profile_form}
    return render(request, "edit_user.html", context)
