# Generated by Django 5.1.1 on 2024-10-19 16:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ride_V3', '0013_alter_payment_currency'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='order_id',
            field=models.BigIntegerField(blank=True, null=True, unique=True),
        ),
    ]
