# Generated by Django 3.0.6 on 2020-07-08 15:34
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [("checkerapp", "0017_alertplugin_active_status")]

    operations = [migrations.RemoveField(model_name="basecheck", name="alert_type")]
