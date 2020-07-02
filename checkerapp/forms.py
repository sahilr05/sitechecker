from django import forms

from .models import BaseCheck
from .models import HttpCheck
from .models import PingCheck
from .models import Service
from .models import TcpCheck

# from django.contrib.auth.models import User
# from .models import Profile

# from django.contrib.auth.forms import UserCreationForm


class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "type": "text"})
        }
        fields = ("name",)


class HttpCheckForm(forms.ModelForm):
    class Meta:
        model = HttpCheck
        widgets = {
            "site_name": forms.TextInput(
                attrs={"class": "form-control", "type": "text"}
            ),
            "expected_status_code": forms.NumberInput(
                attrs={"class": "form-control", "type": "number", "min": 100}
            ),
        }
        fields = ("site_name", "expected_status_code")


class PingCheckForm(forms.ModelForm):
    class Meta:
        model = PingCheck
        widgets = {
            "ip_address": forms.TextInput(
                attrs={"class": "form-control", "type": "text"}
            )
        }
        fields = ("ip_address",)


class TcpCheckForm(forms.ModelForm):
    class Meta:
        model = TcpCheck
        widgets = {
            "ip_address": forms.TextInput(
                attrs={"class": "form-control", "type": "text"}
            ),
            "port": forms.NumberInput(
                attrs={"class": "form-control", "type": "number"}
            ),
        }
        fields = ("ip_address", "port")


class BaseCheckForm(forms.ModelForm):
    class Meta:
        model = BaseCheck
        widgets = {
            "interval": forms.NumberInput(
                attrs={"class": "form-control", "type": "number", "min": 1}
            ),
            "backoff_count": forms.NumberInput(
                attrs={"class": "form-control", "type": "number", "min": 2}
            ),
            "alert_type": forms.Select(attrs={"class": "form-control"}),
            "severe_level": forms.Select(attrs={"class": "form-control"}),
        }
        fields = ("interval", "backoff_count", "severe_level", "alert_type")


# class UserForm(forms.ModelForm):
#     confirm_password = forms.CharField(
#         max_length=32,
#         widget=forms.TextInput(attrs={"class": "form-control", "type": "password"}),
#         required=True,
#     )

#     class Meta:
#         model = User
#         fields = ("username", "email", "password", "confirm_password")


# class EditUserForm(forms.ModelForm):
#     class Meta:
#         model = User
#         fields = ("username", "email")


# class ProfileForm(forms.ModelForm):
#     class Meta:
#         model = Profile
#         widgets = {
#             "phone": forms.TextInput(attrs={"class": "form-control", "type": "text"})
#         }
#         fields = ("phone",)


# class LoginForm(forms.Form):
#     username = forms.CharField(
#         label="Username", widget=forms.TextInput(attrs={"class": "form-control"})
#     )
#     password = forms.CharField(
#         max_length=32,
#         widget=forms.TextInput(attrs={"class": "form-control", "type": "password"}),
#         required=True,
#     )
