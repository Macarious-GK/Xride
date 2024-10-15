from django.db import models
from django.contrib.auth.models import User

class Car(models.Model):
    DOOR_STATUS_CHOICES = [
        ('open', 'Open'),
        ('close', 'Close'),
    ]
    STATUS_CHOICES = (
        ('available', 'Available'),
        ('reserved', 'Reserved'),
    )

    car_name = models.CharField(max_length=50)  # Name of the car
    door_status = models.CharField(max_length=5, choices=DOOR_STATUS_CHOICES, default='close')  # Current status of the car (open/close)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='available')
    latitude = models.DecimalField(max_digits=9, decimal_places=6)  # Car's geographical latitude
    longitude = models.DecimalField(max_digits=9, decimal_places=6)  # Car's geographical longitude

    def __str__(self):
        return f"{self.car_name} - {self.status}"
    def is_reserved(self):
        return self.reserved_by is not None

class Reservation(models.Model):
    # user = models.ForeignKey(User, on_delete=models.CASCADE)  # User who made the reservation
    car = models.OneToOneField(Car, on_delete=models.CASCADE)  # The car that is reserved
    reserved_at = models.DateTimeField(auto_now_add=True)  # Timestamp when the car was reserved
    def __str__(self):
        return f"{self.user.username} reserved {self.car.car_name} at {self.reserved_at}"
