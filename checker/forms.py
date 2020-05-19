from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import *


class UserForm(forms.Form):
    email = forms.EmailField(required=True, widget=forms.TextInput(
        attrs={'class': 'form-control', 'type': 'email'}))
    username = forms.CharField(label="Username", widget=forms.TextInput(
        attrs={'class': 'form-control'}))
    password = forms.CharField(max_length=32, widget=forms.TextInput(
        attrs={'class': 'form-control', 'type': 'password'}), required=True)
    confirm_password = forms.CharField(max_length=32, widget=forms.TextInput(
        attrs={'class': 'form-control', 'type': 'password'}), required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'confirm_password')

class SiteForm(forms.Form):
    site_name = forms.CharField(label="Site name", widget=forms.TextInput(
        attrs={'class': 'form-control'}))
    interval = forms.CharField(label="Interval", widget=forms.TextInput(
        attrs={'class': 'form-control'}))
    number_of_failure = forms.CharField(label="Number of failures", widget=forms.TextInput(
        attrs={'class': 'form-control'}))

class LoginForm(forms.Form):
    username = forms.CharField(
        label="Username", widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(max_length=32, widget=forms.TextInput(
        attrs={'class': 'form-control', 'type': 'password'}), required=True)

class PersonalDetailsForm(forms.Form):
    firstname = forms.CharField(label='First Name', required=True, widget=forms.TextInput(
        attrs={'class': 'form-control', 'type': 'text'}))
    lastname = forms.CharField(label='Last Name', required=True, widget=forms.TextInput(
        attrs={'class': 'form-control', 'type': 'text'}))
    email = forms.CharField(label='Email Address', required=True, widget=forms.TextInput(
        attrs={'class': 'form-control', 'type': 'email'}))
    contact = forms.CharField(label='Contact Number', required=True, widget=forms.TextInput(
        attrs={'class': 'form-control', 'type': 'number'}))

