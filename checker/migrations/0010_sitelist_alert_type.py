# Generated by Django 3.0.6 on 2020-05-28 08:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('checker', '0009_sitelist_maintenance_mode'),
    ]

    operations = [
        migrations.AddField(
            model_name='sitelist',
            name='alert_type',
            field=models.CharField(default='email', max_length=10),
        ),
    ]
