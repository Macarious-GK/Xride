# Generated by Django 5.1.1 on 2024-10-15 21:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ride_V3', '0005_reservation'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='reservation',
            unique_together=set(),
        ),
        migrations.AlterField(
            model_name='reservation',
            name='start_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
