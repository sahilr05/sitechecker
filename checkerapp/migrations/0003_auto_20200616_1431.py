# Generated by Django 3.0.6 on 2020-06-16 14:31
from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    dependencies = [("checkerapp", "0002_remove_checkresult_metadata")]

    operations = [
        migrations.AlterField(
            model_name="basecheck",
            name="interval",
            field=models.IntegerField(default=1),
        )
    ]