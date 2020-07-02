from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.core.validators import RegexValidator
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

# from jsonfield import JSONField


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_regex = RegexValidator(
        regex=r"^\+?1?\d{9,15}$",
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.",
    )
    phone = models.CharField(
        validators=[phone_regex],
        max_length=15,
        blank=False,
        unique=True,  # validators should be a list
    )
    telegram_id = models.CharField(null=True, max_length=50)
    active_status = models.BooleanField(default=True)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


class BaseCheck(models.Model):
    NORMAL, WARNING, CRITICAL = list(range(3))
    SEVERE_CHOICES = ((NORMAL, "NORMAL"), (WARNING, "WARNING"), (CRITICAL, "CRITICAL"))

    EMAIL, TELEGRAM, SMS = list(range(3))
    ALERT_CHOICES = ((EMAIL, "EMAIL"), (TELEGRAM, "TELEGRAM"), (SMS, "SMS"))

    interval = models.IntegerField(default=1)
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
