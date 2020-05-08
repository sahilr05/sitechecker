from django.db import models
from django.contrib.auth.models import User
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

class PersonalDetails(models.Model):
    firstname = models.CharField(max_length=50)
    lastname = models.CharField(max_length=50)
    email = models.CharField(max_length=100)
    contact = models.DecimalField(max_digits=10, decimal_places=0)

    def __str__(self):
        return self.email

class SiteList(models.Model):
    site_name = models.CharField(max_length=30, unique=True)
    admin = models.ForeignKey(PersonalDetails, related_name='sitelist',on_delete=models.CASCADE)
    interval = models.IntegerField()
    # owner = models.ForeignKey(User,related_name='list', on_delete=models.CASCADE)

    def __str__(self):
        return self.site_name

class PingInfo(models.Model):
    DOWN, UP = list(range(2))
    STATUS_CHOICES = ((UP, "UP"), (DOWN, "DOWN"))
    status = models.SmallIntegerField(choices=STATUS_CHOICES)
    site = models.ForeignKey(SiteList, on_delete=models.CASCADE)
    # status = models.TextField(max_length=10)
    time = models.DateTimeField(auto_now_add=True)

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