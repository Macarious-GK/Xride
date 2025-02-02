import os
from django.utils import timezone
from django.conf import settings
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models

def personal_photo_upload_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{instance.username}_personal_{timezone.now().strftime('%Y-%m-%d-%H-%M-%S)')}.{ext}"
    return os.path.join('media', 'personal', filename)

def licence_photo_upload_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{instance.username}_licence_{timezone.now().strftime('%Y-%m-%d-%H-%M-%S)')}.{ext}"
    return os.path.join('media', 'licence', filename)

def national_id_photo_upload_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{instance.username}_national_id_{timezone.now().strftime('%Y-%m-%d-%H-%M-%S)')}.{ext}"
    return os.path.join('media', 'national_id', filename)

def violation_photo_upload_path(instance, filename):
    ext = filename.split('.')[-1]  # Get file extension
    filename = f"violation_{instance.id}_{timezone.now().strftime('%Y-%m-%d-%H-%M-%S')}.{ext}"
    return os.path.join('media', 'violation_photos', filename)

class User(AbstractUser):
    wallet_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    phone_number = models.CharField(max_length=15, unique=True, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    national_id = models.CharField(max_length=14, unique=True, blank=True, null=True)  # National ID field
    verified = models.BooleanField(default=False)


    personal_photo = models.ImageField(upload_to=personal_photo_upload_path, blank=True, null=True)
    licence_photo = models.ImageField(upload_to=licence_photo_upload_path, blank=True, null=True)
    national_id_photo = models.ImageField(upload_to=national_id_photo_upload_path, blank=True, null=True)

    groups = models.ManyToManyField(
        Group,
        related_name='xrideuser_set',  # Custom related name
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.'
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='xrideuser_set',  # Custom related name
        blank=True,
        help_text='Specific permissions for this user.'
    )

    def save(self, *args, **kwargs):
        if self.username:
            self.username = self.username.lower()  # Convert to lowercase
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Name: {self.username} Balance: {self.wallet_balance}"

class Location(models.Model):
    park_name = models.CharField(max_length=255)
    radius = models.FloatField(help_text="Radius of the park in meters")
    latitude = models.FloatField(help_text="Latitude of the park location")
    longitude = models.FloatField(help_text="Longitude of the park location")

    def __str__(self):
        return f"{self.park_name} (Radius: {self.radius}) with ID: {self.id}"

class Payment(models.Model):
    STATUS_CHOICES = [
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('pending', 'Pending'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    transaction_id = models.BigIntegerField(unique=True, null=True, blank=True)  # Allow null values for initial creation
    order_id = models.TextField(unique=True)
    collector = models.CharField(max_length=255, null=True, blank=True)  # Nullable
    card_type = models.CharField(max_length=20, blank=True, null=True)  # e.g., 'Visa', 'MasterCard'
    card_last_four = models.CharField(max_length=4, blank=True, null=True)  # Last four digits of the card
    currency = models.CharField(max_length=3, blank=True, null=True)  # e.g., 'EGP'
    amount = models.DecimalField(max_digits=10, decimal_places=2)  # Transaction amount
    created_at = models.DateTimeField(auto_now_add=True)  # Automatically set to now when created
    txn_response_code = models.CharField(max_length=10, null=True, blank=True)  # Nullable for initial creation
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')  # Default to 'pending'

    def __str__(self):
        return f"{self.user} :- Transaction {self.transaction_id} - order_id {self.order_id} - {self.amount} {self.currency} - Status: {self.status}"

class Reservation(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    PLAN_CHOICES = [
        ('2H', '2 Hours'),
        ('6H', '6 Hours'),
        ('12H', '12 Hours'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    car = models.ForeignKey('Car', on_delete=models.CASCADE)
    reservation_Locatiion_Source = models.ForeignKey('Location', on_delete=models.CASCADE)
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)  # Will be set when releasing the reservation
    reservation_plan = models.CharField(max_length=3, choices=PLAN_CHOICES)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    duration = models.FloatField(null=True, blank=True)  # Duration in hours

    def __str__(self):
        return f"Reservation {self.id} for {self.car} ({self.status}) by {self.user}"

    class Meta:
        ordering = ['start_time']  # Ensures reservations are ordered by start time.

class ReservationHistory(models.Model):
    STATUS_CHOICES = [
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    PLAN_CHOICES = [
        ('2H', '2 Hours'),
        ('6H', '6 Hours'),
        ('12H', '12 Hours'),
    ]
    reservation_ID = models.IntegerField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    car = models.ForeignKey('Car', on_delete=models.CASCADE)
    reservation_Locatiion_Source = models.ForeignKey(
        Location,
        on_delete=models.CASCADE,
        related_name='source_reservations'
    )
    reservation_Locatiion_Distnation = models.ForeignKey(
        Location,
        on_delete=models.CASCADE,
        related_name='destination_reservations'
    )
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    reservation_plan = models.CharField(max_length=3, choices=PLAN_CHOICES)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='completed')
    duration = models.FloatField()
    review_rate = models.PositiveIntegerField(
        choices=[(i, i) for i in range(1, 6)],
        help_text="Review rate from 1 to 5",null=True,blank=True
    )
    review_text = models.TextField(help_text="Review text about the park", null=True,blank=True)


    def __str__(self):
        return f"History of Reservation {self.reservation_ID} for {self.user} ({self.status}) for car {self.car.car_model.model_name} ({self.car.car_plate}) by {self.car.car_model.year}"

    class Meta:
        ordering = ['start_time']  # Ensures history is ordered by start time

class Fine(models.Model):
    class Status(models.TextChoices):
        PAID = 'paid', 'Paid'
        PENDING = 'pending', 'Pending'
        UNPAID = 'unpaid', 'Unpaid'

    reservation = models.ForeignKey('ReservationHistory', on_delete=models.CASCADE)
    car = models.ForeignKey('Car', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    description = models.TextField()  # Detailed information about the fine
    created_at = models.DateTimeField(auto_now_add=True)  # Automatically set when the fine is created
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    
    # Field to store the traffic violation copy image
    violation_copy = models.ImageField(upload_to=violation_photo_upload_path, null=True, blank=True)

    def __str__(self):
        return f"Fine {self.id} for Reservation {self.reservation.id} - {self.amount}"

    class Meta:
        ordering = ['created_at']  # Sort fines by the creation date, so the most recent is first

class ThirdPartyMaintenance(models.Model):
    name = models.CharField(max_length=255)
    maintenance_type = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name} ({self.maintenance_type})"

class CarModel(models.Model):
    ENGINE_TYPE = [
        ('electric', 'Electric'),
        ('diesel', 'Diesel'),
    ]

    model_name = models.CharField(max_length=255, unique=True, help_text='e.g., Tesla Model 3, Ford Focus')
    manufacturer = models.CharField(max_length=255)
    year = models.PositiveIntegerField()
    engine_type = models.CharField(max_length=50, choices=ENGINE_TYPE, default='diesel')
    seating_capacity = models.IntegerField()
    additional_features = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.model_name} ({self.manufacturer}, {self.year})"

class Car(models.Model):
    DOOR_STATUS_CHOICES = [
        ('locked', 'Locked'),
        ('unlocked', 'Unlocked'),
    ]

    RESERVATION_STATUS_CHOICES = [
        ('reserved', 'Reserved'),
        ('maintenance', 'Maintenance'),
        ('available', 'Available'),
    ]
    Engine_STATUS_CHOICES = [
        ('off', 'Off'),
        ('on', 'On'),
    ]

    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    car_model = models.ForeignKey(CarModel, on_delete=models.CASCADE)
    car_plate = models.CharField(max_length=20, unique=True)
    door_status = models.CharField(max_length=10, choices=DOOR_STATUS_CHOICES, default='locked')
    engine_status = models.CharField(max_length=10, choices=Engine_STATUS_CHOICES, default='off')
    # oil_temperature = models.FloatField(help_text="Oil temperature in °C")
    speed = models.FloatField(default=0.0, help_text="Speed in km/h")
    distance_traveled = models.FloatField(default=0.0, help_text="Distance in km")
    fuel_level = models.FloatField(default=100.0, help_text="Fuel level in %")
    # temperature = models.FloatField()
    location_latitude = models.FloatField()
    location_longitude = models.FloatField()
    reservation_status = models.CharField(max_length=12, choices=RESERVATION_STATUS_CHOICES, default='available')
    booking_price_2H = models.DecimalField(max_digits=8, decimal_places=2)
    booking_price_6H = models.DecimalField(max_digits=8, decimal_places=2)
    booking_price_12H = models.DecimalField(max_digits=8, decimal_places=2)
    
    def __str__(self):
        return f"ID: {self.id} Model: {self.car_model} - Plate: {self.car_plate} - status: {self.reservation_status}"

class Maintenance(models.Model):
    class MaintenanceType(models.TextChoices):
        OIL_CHANGE = 'oil_change', 'Oil Change'
        Cleaning = 'clean', 'Clean'
        TIRE_ROTATION = 'tire_rotation', 'Tire Rotation'
        TIRE_REPLACEMENT = 'tire_replacement', 'Tire Replacement'
        BRAKE_INSPECTION = 'brake_inspection', 'Brake Inspection'
        BATTERY_REPLACEMENT = 'battery_replacement', 'Battery Replacement'
        ENGINE_TUNING = 'engine_tuning', 'Engine Tuning'
        FLUID_CHECK = 'fluid_check', 'Fluid Check'
        FILTER_CHANGE = 'filter_change', 'Filter Change'
        SUSPENSION_INSPECTION = 'suspension_inspection', 'Suspension Inspection'
        ALIGNMENT = 'alignment', 'Alignment'
        AIR_CONDITIONING_SERVICE = 'ac_service', 'A/C Service'
        LIGHTS_CHECK = 'lights_check', 'Lights Check'
        GENERAL_INSPECTION = 'general_inspection', 'General Inspection'
        OTHER = 'other', 'Other'

    car = models.ForeignKey('Car', on_delete=models.CASCADE)
    maintenance_type = models.CharField(
        max_length=50,
        choices=MaintenanceType.choices,
        help_text='Type of maintenance, e.g., oil change, tire rotation'
    )
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    performed_at = models.DateTimeField()
    notes = models.TextField(blank=True, null=True)
    performed_by = models.ForeignKey('ThirdPartyMaintenance', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.maintenance_type} for {self.car} by {self.performed_by}"

# class UserActionLog(models.Model):
#     ACTION_CHOICES = [
#         ('reservation_created', 'Reservation Created'),
#         ('reservation_updated', 'Reservation Updated'),
#         ('reservation_deleted', 'Reservation Deleted'),
#         ('payment_made', 'Payment Made'),
#         ('profile_updated', 'Profile Updated'),
#         ('fine_paid', 'Fine Paid'),
#         ('car_booked', 'Car Booked'),
#         ('car_returned', 'Car Returned'),
#         ('violation_reported', 'Violation Reported'),
#     ]

#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     action_type = models.CharField(max_length=50, choices=ACTION_CHOICES)
#     action_details = models.TextField(null=True, blank=True)  # Any additional details about the action
#     timestamp = models.DateTimeField(auto_now_add=True)  # Automatically set the timestamp when the log is created

#     def __str__(self):
#         return f"{self.user.username} performed {self.action_type} at {self.timestamp}"

#     class Meta:
#         ordering = ['-timestamp']  # Orders the logs by the most recent first





# class Reservation(models.Model):
#     STATUS_CHOICES = [
#         ('active', 'Active'),
#         ('completed', 'Completed'),
#         ('cancelled', 'Cancelled'),
#     ]
    
#     PLAN_CHOICES = [
#         ('2H', '2 Hours'),
#         ('6H', '6 Hours'),
#         ('12H', '12 Hours'),
#     ]

    # user = models.ForeignKey(User, on_delete=models.CASCADE)
    # car = models.ForeignKey('Car', on_delete=models.CASCADE)
    # start_time = models.DateTimeField(null=True, blank=True)
    # end_time = models.DateTimeField(null=True, blank=True)  # Will be set when releasing the reservation
    # reservation_plan = models.CharField(max_length=3, choices=PLAN_CHOICES)
    # status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    # duration = models.FloatField(null=True, blank=True)  # Duration in hours
    # def __str__(self):
    #     return f"{self.user.username} - {self.car.car_name} ({self.status})"



# class Car(models.Model):
    # DOOR_STATUS_CHOICES = [
    #     ('locked', 'Locked'),
    #     ('unlocked', 'Unlocked'),
    # ]

    # RESERVATION_STATUS_CHOICES = [
    #     ('reserved', 'Reserved'),
    #     ('available', 'Available'),
    # ]

#     car_name = models.CharField(max_length=100)
#     car_plate = models.CharField(max_length=20, unique=True)
#     year = models.PositiveIntegerField()
#     door_status = models.CharField(max_length=10, choices=DOOR_STATUS_CHOICES, default='locked')
#     temperature = models.FloatField()  # Celsius temperature
#     location_latitude = models.FloatField()
#     location_longitude = models.FloatField()
#     reservation_status = models.CharField(max_length=10, choices=RESERVATION_STATUS_CHOICES, default='available')
#     booking_price_2H = models.DecimalField(max_digits=8, decimal_places=2)
#     booking_price_6H = models.DecimalField(max_digits=8, decimal_places=2)
#     booking_price_12H = models.DecimalField(max_digits=8, decimal_places=2)

#     def __str__(self):
#         return f"ID: {self.id} Name: {self.car_name} - Year: {self.year} - Temp: {self.temperature} - status: {self.reservation_status}"





