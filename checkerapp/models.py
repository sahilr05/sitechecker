from django.contrib.auth.models import User
from django.db import models


class SiteList(models.Model):
    site_name = models.CharField(
        max_length=30, unique=True
    )  # only for HTTP.. for TCP and PING use IP / DNS
    admin = models.ForeignKey(User, related_name="sitelist", on_delete=models.CASCADE)
    users = models.ManyToManyField(
        User, related_name="sitelist_users"
    )  # For difference services
    interval = models.CharField(max_length=10)
    failure_count = models.IntegerField()
    alert_type = models.CharField(max_length=10, default="email")  # diff model
    maintenance_mode = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.site_name}"


class PingInfo(models.Model):  # CheckStatusInfo
    DOWN, UP = list(range(2))
    STATUS_CHOICES = ((UP, "UP"), (DOWN, "DOWN"))
    status = models.SmallIntegerField(choices=STATUS_CHOICES)
    site = models.ForeignKey(SiteList, on_delete=models.CASCADE)
    date_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.status
