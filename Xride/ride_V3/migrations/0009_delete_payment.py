# Generated by Django 5.1.1 on 2024-10-17 20:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ride_V3', '0008_remove_payment_card_last_digits_and_more'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Payment',
        ),
    ]
