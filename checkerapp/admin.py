from django.contrib import admin

from .models import BaseCheck
from .models import CheckResult
from .models import HttpCheck
from .models import PingCheck
from .models import Service
from .models import TcpCheck

myModels = [Service, BaseCheck, HttpCheck, TcpCheck, PingCheck, CheckResult]
admin.site.register(myModels)
