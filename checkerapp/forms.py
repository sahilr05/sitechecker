from django import forms
from django.contrib.auth.models import User

from .models import BaseCheck
from .models import HttpCheck

# from .models import PingCheck
# from .models import TcpCheck
# from django.contrib.auth.forms import UserCreationForm

ALERT_CHOICES = (("email", "Email"), ("phone", "Phone"), ("both", "Both"))


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


class PingCheckForm(forms.Form):
    ip_address = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control", "type": "text"}),
    )


class TcpCheckForm(forms.Form):
    ip_address = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control", "type": "text"}),
    )


class BaseCheckForm(forms.ModelForm):
    interval = forms.IntegerField(
        required=True,
        widget=forms.NumberInput(
            attrs={"class": "form-control", "type": "number", "value": "5"}
        ),
    )
    backoff_count = forms.IntegerField(
        required=True,
        widget=forms.NumberInput(
            attrs={"class": "form-control", "type": "number", "value": "3"}
        ),
    )

    class Meta:
        model = BaseCheck
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


# class SiteForm(forms.ModelForm):
#     alert_type = forms.ChoiceField(choices=ALERT_CHOICES, required=True)

#     class Meta:
#         model = SiteList
#         fields = ("site_name", "interval", "failure_count", "alert_type")


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
