# Generated by Django 3.0.6 on 2020-05-24 06:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('checker', '0008_auto_20200521_0813'),
    ]

    operations = [
        migrations.AddField(
            model_name='sitelist',
            name='maintenance_mode',
            field=models.IntegerField(default=0),
        ),
    ]