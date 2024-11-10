# Generated by Django 5.1.1 on 2024-11-09 23:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ride_V3', '0021_useractionlog'),
    ]

    operations = [
        migrations.AlterField(
            model_name='maintenance',
            name='maintenance_type',
            field=models.CharField(choices=[('oil_change', 'Oil Change'), ('clean', 'Clean'), ('tire_rotation', 'Tire Rotation'), ('tire_replacement', 'Tire Replacement'), ('brake_inspection', 'Brake Inspection'), ('battery_replacement', 'Battery Replacement'), ('engine_tuning', 'Engine Tuning'), ('fluid_check', 'Fluid Check'), ('filter_change', 'Filter Change'), ('suspension_inspection', 'Suspension Inspection'), ('alignment', 'Alignment'), ('ac_service', 'A/C Service'), ('lights_check', 'Lights Check'), ('general_inspection', 'General Inspection'), ('other', 'Other')], help_text='Type of maintenance, e.g., oil change, tire rotation', max_length=50),
        ),
    ]