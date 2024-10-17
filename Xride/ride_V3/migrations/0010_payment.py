# Generated by Django 5.1.1 on 2024-10-17 20:37

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ride_V3', '0009_delete_payment'),
    ]

    operations = [
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('transaction_id', models.BigIntegerField(unique=True)),
                ('order_id', models.BigIntegerField()),
                ('collector', models.CharField(max_length=255)),
                ('card_type', models.CharField(blank=True, max_length=20, null=True)),
                ('card_last_four', models.CharField(blank=True, max_length=4, null=True)),
                ('currency', models.CharField(max_length=3)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('created_at', models.DateTimeField()),
                ('txn_response_code', models.CharField(max_length=10)),
                ('status', models.CharField(choices=[('success', 'Success'), ('failed', 'Failed'), ('pending', 'Pending')], max_length=10)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payments', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
