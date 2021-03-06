# Generated by Django 3.0.6 on 2020-07-02 06:15
from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    dependencies = [("checkerapp", "0010_auto_20200701_0659")]

    operations = [
        migrations.AddField(
            model_name="profile",
            name="active_status",
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name="alertsent",
            name="sent_at",
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
