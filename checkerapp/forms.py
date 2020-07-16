from django import forms

from .models import BaseCheck
from .models import HttpCheck
from .models import PingCheck
from .models import Service
from .models import TcpCheck


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
