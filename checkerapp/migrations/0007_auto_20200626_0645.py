# Generated by Django 3.0.6 on 2020-06-26 06:45
import django.core.validators
from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    dependencies = [("checkerapp", "0006_profile")]

    operations = [
        migrations.AlterField(
            model_name="profile",
            name="phone",
            field=models.CharField(
                max_length=15,
                validators=[
                    django.core.validators.RegexValidator(
                        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.",
                        regex="^\\+?1?\\d{9,15}$",
                    )
                ],
            ),
        )
    ]
