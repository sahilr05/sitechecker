from django import forms
from django.contrib.auth.models import User

from .models import BaseCheck
from .models import HttpCheck
from .models import PingCheck
from .models import Profile
from .models import Service
from .models import TcpCheck

# from django.contrib.auth.forms import UserCreationForm

ALERT_CHOICES = (("email", "Email"), ("phone", "Phone"), ("both", "Both"))


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
                attrs={"class": "form-control", "type": "number"}
            ),
        }
        fields = ("site_name", "expected_status_code")


class PingCheckForm(forms.ModelForm):
    class Meta:
        model = PingCheck
        fields = ("ip_address",)


class TcpCheckForm(forms.ModelForm):
    class Meta:
        model = TcpCheck
        fields = ("ip_address", "port")


class BaseCheckForm(forms.ModelForm):
    class Meta:
        model = BaseCheck
        widgets = {
            "interval": forms.NumberInput(
                attrs={"class": "form-control", "type": "number"}
            ),
            "backoff_count": forms.NumberInput(
                attrs={"class": "form-control", "type": "number"}
            ),
        }
        fields = ("interval", "backoff_count", "severe_level", "alert_type")


class UserForm(forms.ModelForm):
    confirm_password = forms.CharField(
        max_length=32,
        widget=forms.TextInput(attrs={"class": "form-control", "type": "password"}),
        required=True,
    )

    class Meta:
        model = User
        fields = ("username", "email", "password", "confirm_password")


class EditUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("username", "email")


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ("phone",)


class LoginForm(forms.Form):
    username = forms.CharField(
        label="Username", widget=forms.TextInput(attrs={"class": "form-control"})
    )
    password = forms.CharField(
        max_length=32,
        widget=forms.TextInput(attrs={"class": "form-control", "type": "password"}),
        required=True,
    )


class PersonalDetailsForm(forms.Form):
    firstname = forms.CharField(
        label="First Name",
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control", "type": "text"}),
    )
    lastname = forms.CharField(
        label="Last Name",
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control", "type": "text"}),
    )
    email = forms.CharField(
        label="Email Address",
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control", "type": "email"}),
    )
    contact = forms.CharField(
        label="Contact Number",
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control", "type": "number"}),
    )
