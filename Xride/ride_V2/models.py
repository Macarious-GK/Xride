from django.db import models

class Car(models.Model):
    DOOR_STATUS_CHOICES = [
        ('locked', 'Locked'),
        ('unlocked', 'Unlocked'),
    ]
    temp = models.FloatField(default=0.0)  # Temperature
    door_status = models.CharField(max_length=8, choices=DOOR_STATUS_CHOICES, default='close')  # Current status of the car (open/close)
    gas = models.FloatField(default=0.0) # Gas level
    def __str__(self):
        return f'Car {self.id}: Temp={self.temp}, Door={self.door_status}, Gas={self.gas}'
