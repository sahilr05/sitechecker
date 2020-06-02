# Generated by Django 3.0.6 on 2020-05-15 10:49

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("checker", "0002_auto_20200509_1754"),
    ]

    operations = [
        migrations.DeleteModel(name="PersonalDetails",),
        migrations.AddField(
            model_name="sitelist",
            name="users",
            field=models.ManyToManyField(
                related_name="sitelist_users", to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.DeleteModel(name="PingInfo",),
    ]
