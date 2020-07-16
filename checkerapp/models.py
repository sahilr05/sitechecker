import logging

from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from polymorphic.models import PolymorphicModel

logger = logging.getLogger(__name__)

# from jsonfield import JSONField


class BaseCheck(models.Model):
    WARNING, CRITICAL = list(
        range(2)
    )  # Replace normal with warning...warning with critical
    SEVERE_CHOICES = ((WARNING, "WARNING"), (CRITICAL, "CRITICAL"))

    interval = models.IntegerField(default=1)
    backoff_count = models.IntegerField(default=3)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    severe_level = models.SmallIntegerField(choices=SEVERE_CHOICES, default=0)
    creator = models.ForeignKey(
        User, related_name="commoninfo_creator", on_delete=models.CASCADE
    )
    maintenance_mode = models.BooleanField(default=False)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.CharField(max_length=50)
    content_object = GenericForeignKey("content_type", "object_id")

    def __str__(self):
        return f"{self.content_object}"


class AlertPlugin(PolymorphicModel):
    active_status = models.BooleanField(default=True)
    alert_receiver = models.ForeignKey(
        User, related_name="alert_receiver", on_delete=models.CASCADE
    )


class PluginList(models.Model):
    name = models.CharField(max_length=50)
    active_status = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name}"


class Service(models.Model):
    warning_severity = models.ManyToManyField(
        PluginList, related_name="warnign_plugin_list"
    )
    critical_severity = models.ManyToManyField(
        PluginList, related_name="critical_plugin_list"
    )

    name = models.CharField(max_length=50, unique=True)
    users = models.ManyToManyField(User, related_name="service_users")
    checks = models.ManyToManyField(BaseCheck)


class CheckResult(models.Model):
    FAILURE, SUCCESS = list(range(2))
    RESULT_CHOICES = ((SUCCESS, "SUCCESS"), (FAILURE, "FAILURE"))

    result = models.SmallIntegerField(choices=RESULT_CHOICES)
    # metadata = JSONField()
    created_at = models.DateTimeField(auto_now_add=True)


class AlertSent(models.Model):
    check_obj = models.ForeignKey(BaseCheck, on_delete=models.CASCADE)
    sent_at = models.DateTimeField(auto_now_add=True)


class AbstractCheck(models.Model):
    base_check = GenericRelation(BaseCheck)
    results = models.ManyToManyField(CheckResult)

    class Meta:
        abstract = True

    @staticmethod
    def execute():
        raise NotImplementedError()


class HttpCheck(AbstractCheck):
    site_name = models.CharField(max_length=50, unique=True, default="https://")
    expected_status_code = models.IntegerField()

    def __str__(self):
        return f"{self.site_name}"

    @staticmethod
    def execute():
        pass


class PingCheck(AbstractCheck):
    ip_address = models.GenericIPAddressField()

    def __str__(self):
        return f"{self.ip_address}"

    @staticmethod
    def execute():
        pass


class TcpCheck(AbstractCheck):
    ip_address = models.GenericIPAddressField()
    port = models.IntegerField(default=443)

    def __str__(self):
        return f"{self.ip_address}"

    @staticmethod
    def execute():
        pass
