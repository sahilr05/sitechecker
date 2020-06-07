# Generated by Django 3.0.6 on 2020-05-17 19:15
from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    dependencies = [("checkerapp", "0005_auto_20200517_1908")]

    operations = [
        migrations.AddField(
            model_name="pinginfo",
            name="status",
            field=models.CharField(
                choices=[("UP", "UP"), ("DOWN", "DOWN")], default=1, max_length=50
            ),
            preserve_default=False,
        )
    ]