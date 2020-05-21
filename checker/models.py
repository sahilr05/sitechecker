from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django_celery_results.models import TaskResult


class SiteList(models.Model):
    site_name = models.CharField(max_length=30, unique=True)
    admin = models.ForeignKey(User, related_name='sitelist',on_delete=models.CASCADE)
    users = models.ManyToManyField(User, related_name = 'sitelist_users')
    interval = models.CharField(max_length=10)
    failure_count = models.IntegerField()

    def __str__(self):
        return f"{self.site_name}"
        # self.site_name,self.users

class PingInfo(models.Model):
    # DOWN, UP = list(range(2))
    STATUS_CHOICES = (('UP', "UP"), ('DOWN', "DOWN")) 
    status = models.CharField(max_length=50, choices=STATUS_CHOICES)
    site = models.ForeignKey(SiteList, on_delete=models.CASCADE)
    date_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.status
    

# class Topic(models.Model):
#     subject = models.CharField(max_length=255)
#     last_updated = models.DateTimeField(auto_now_add=True)
#     board = models.ForeignKey(Board, related_name='topics')
#     starter = models.ForeignKey(User, related_name='topics')


# class Post(models.Model):
#     message = models.TextField(max_length=4000)
#     topic = models.ForeignKey(Topic, related_name='posts')
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(null=True)
#     created_by = models.ForeignKey(User, related_name='posts')
#     updated_by = models.ForeignKey(User, null=True, related_name='+')