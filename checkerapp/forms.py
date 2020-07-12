from django import forms

from .models import BaseCheck
from .models import HttpCheck
from .models import PingCheck
from .models import PluginList
from .models import Service
from .models import TcpCheck


def get_plugins():
    plugin_list = PluginList.objects.all()
    return plugin_list


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
            "severe_level": forms.Select(attrs={"class": "form-control"}),
        }
        fields = ("interval", "backoff_count", "severe_level")


# def get_plugins():
#     EMAIL, SMS = list(range(2))
#     PLUGIN_CHOICES = ((EMAIL, "EMAIL"), (SMS, "SMS"))
#     custom_plugins = [cls.__name__ for cls in AlertPlugin.__subclasses__()]
#     for plugin_number, plugin in zip(range(2,len(custom_plugins)+2), custom_plugins):
#         temp = (plugin_number, plugin)
#         PLUGIN_CHOICES += tuple((temp,),)
#     return PLUGIN_CHOICES

# # def get_plugins():
# #     plugin_list = list(PluginList.objects.values_list('name', flat=True))
# #     return plugin_list


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

# name = forms.CharField(
#     widget=forms.TextInput(attrs={'class': 'form-control'})
# )
# warning_severity = forms.MultipleChoiceField(
#     required=False,
#     widget=forms.CheckboxSelectMultiple(attrs={'class': 'checkbox', 'min':2}),
#     # choices=get_plugins(),
#     initial=0,
# )
# critical_severity = forms.MultipleChoiceField(
#     required=False,
#     widget=forms.CheckboxSelectMultiple(attrs={'class': 'checkbox'}),
#     choices=get_plugins(),
#     initial=0,


# class ServiceForm(forms.ModelForm):
#     class Meta:
#         model = Service
#         widgets = {
#             "name": forms.TextInput(attrs={"class": "form-control", "type": "text"}),
#             # "critical_severity": forms.Select(attrs={"class": "selectpicker form-control"}, choices=get_plugins()),
#             'warning_severity': forms.CheckboxSelectMultiple(attrs={"class": "form-control field-checks", "type":"checkbox"}, choices=get_plugins())
#         }
#         fields = ("name", 'warning_severity')
# )
