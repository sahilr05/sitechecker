# Generated by Django 3.0.6 on 2020-07-07 04:30
from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    dependencies = [("checkerapp", "0016_remove_alertplugin_check_obj")]

    operations = [
        migrations.AddField(
            model_name="alertplugin",
            name="active_status",
            field=models.BooleanField(default=True),
        )
    ]
