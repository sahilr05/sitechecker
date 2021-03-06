# Generated by Django 3.0.6 on 2020-07-01 06:37
import django.db.models.deletion
from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    dependencies = [("checkerapp", "0008_auto_20200627_1543")]

    operations = [
        migrations.AlterField(
            model_name="basecheck",
            name="alert_type",
            field=models.SmallIntegerField(
                choices=[(0, "EMAIL"), (1, "TELEGRAM"), (2, "SMS")], default=0
            ),
        ),
        migrations.CreateModel(
            name="AlertSent",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("sent_at", models.DateTimeField()),
                (
                    "check_id",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="checkerapp.BaseCheck",
                    ),
                ),
            ],
        ),
    ]
