# Generated by Django 5.1.1 on 2024-10-01 09:08

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address', models.CharField(max_length=255)),
                ('city', models.CharField(max_length=100)),
                ('latitude', models.DecimalField(decimal_places=6, max_digits=9)),
                ('longitude', models.DecimalField(decimal_places=6, max_digits=9)),
            ],
        ),
        migrations.CreateModel(
            name='Car',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('make', models.CharField(max_length=101)),
                ('model', models.CharField(max_length=100)),
                ('year', models.IntegerField()),
                ('license_plate', models.CharField(max_length=15, unique=True)),
                ('status', models.CharField(choices=[('available', 'Available'), ('rented', 'Rented'), ('maintenance', 'Maintenance')], default='available', max_length=20)),
                ('location', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cars', to='ride_V0.location')),
            ],
        ),
    ]