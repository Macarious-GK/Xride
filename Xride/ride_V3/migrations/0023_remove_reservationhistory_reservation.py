# Generated by Django 5.1.1 on 2024-11-09 23:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ride_V3', '0022_alter_maintenance_maintenance_type'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='reservationhistory',
            name='reservation',
        ),
    ]