# Generated by Django 3.0.6 on 2020-05-19 11:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("checker", "0006_pinginfo_status"),
    ]

    operations = [
        migrations.AddField(
            model_name="sitelist",
            name="failure_count",
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
    ]
