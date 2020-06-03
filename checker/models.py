from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django_celery_results.models import TaskResult


class SiteList(models.Model):
    site_name = models.CharField(max_length=30, unique=True)
    admin = models.ForeignKey(User, related_name="sitelist", on_delete=models.CASCADE)
    users = models.ManyToManyField(User, related_name="sitelist_users")
    interval = models.CharField(max_length=10)
    failure_count = models.IntegerField()
    alert_type = models.CharField(max_length=10, default="email")
    maintenance_mode = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.site_name}"


class PingInfo(models.Model):
    STATUS_CHOICES = (("UP", "UP"), ("DOWN", "DOWN"))
    status = models.CharField(max_length=50, choices=STATUS_CHOICES)
    site = models.ForeignKey(SiteList, on_delete=models.CASCADE)
    date_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.status
