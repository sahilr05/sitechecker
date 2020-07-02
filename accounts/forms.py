from django import forms
from django.contrib.auth.models import User

from checkerapp.models import Profile


class UserForm(forms.ModelForm):
    confirm_password = forms.CharField(
        max_length=32,
        widget=forms.TextInput(attrs={"class": "form-control", "type": "password"}),
        required=True,
    )

    class Meta:
        model = User
        fields = ("username", "email", "password", "confirm_password")


class MyAccountForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "username")


class EditUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("username", "email")


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        widgets = {
            "phone": forms.TextInput(attrs={"class": "form-control", "type": "text"})
        }
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
