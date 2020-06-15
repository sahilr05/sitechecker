from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models

# from jsonfield import JSONField


class BaseCheck(models.Model):
    NORMAL, WARNING, CRITICAL = list(range(3))
    SEVERE_CHOICES = ((NORMAL, "NORMAL"), (WARNING, "WARNING"), (CRITICAL, "CRITICAL"))

    EMAIL, WHATSAPP, SLACK = list(range(3))
    ALERT_CHOICES = ((EMAIL, "EMAIL"), (WHATSAPP, "WHATSAPP"), (SLACK, "SLACK"))

    interval = models.IntegerField()
    backoff_count = models.IntegerField(default=3)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    severe_level = models.SmallIntegerField(choices=SEVERE_CHOICES, default=0)
    alert_type = models.SmallIntegerField(choices=ALERT_CHOICES, default=0)
    creator = models.ForeignKey(
        User, related_name="commoninfo_creator", on_delete=models.CASCADE
    )
    maintenance_mode = models.BooleanField(default=False)
    users = models.ManyToManyField(User)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.CharField(max_length=50)
    content_object = GenericForeignKey("content_type", "object_id")


class Service(models.Model):
    name = models.CharField(max_length=50, unique=True)
    checks = models.ManyToManyField(BaseCheck)


class CheckResult(models.Model):
    FAILURE, SUCCESS = list(range(2))
    RESULT_CHOICES = ((SUCCESS, "SUCCESS"), (FAILURE, "FAILURE"))

    result = models.SmallIntegerField(choices=RESULT_CHOICES)
    # metadata = JSONField()
    created_at = models.DateField(auto_now_add=True)


class AbstractCheck(models.Model):
    base_check = GenericRelation(BaseCheck)
    results = models.ManyToManyField(CheckResult)

    class Meta:
        abstract = True

    @staticmethod
    def execute():
        raise NotImplementedError()


class HttpCheck(AbstractCheck):
    site_name = models.CharField(max_length=50, unique=True)
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

    def __str__(self):
        return f"{self.ip_address}"

    @staticmethod
    def execute():
        pass
