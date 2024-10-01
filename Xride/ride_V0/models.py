from django.db import models

class Car(models.Model):
    brand = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    year = models.IntegerField()
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.brand} {self.model} ({self.year})"

# # Create your models here.
# class Location(models.Model):
#     address = models.CharField(max_length=255)
#     city = models.CharField(max_length=100)
#     latitude = models.DecimalField(max_digits=9, decimal_places=6)
#     longitude = models.DecimalField(max_digits=9, decimal_places=6)

#     def __str__(self):
#         return f"{self.address}, {self.city}"

# class Car(models.Model):
#     STATUS_CHOICES = (
#         ('available', 'Available'),
#         ('rented', 'Rented'),
#         ('maintenance', 'Maintenance'),
#     )

#     make = models.CharField(max_length=101)
#     model = models.CharField(max_length=100)
#     year = models.IntegerField()
#     license_plate = models.CharField(max_length=15, unique=True)
#     status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
#     location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='cars')

#     def __str__(self):
#         return f"{self.make} {self.model} ({self.license_plate})"
