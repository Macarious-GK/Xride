# ride_V3/serializers.py

from rest_framework import serializers
from .models import *

class XrideUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = XrideUser
        fields = ['id', 'username', 'email', 'first_name', 'last_name','wallet_balance', 'phone_number', 'address','national_id']
        extra_kwargs = {
            'password': {'write_only': True},
            'groups': {'required': False},
            'user_permissions': {'required': False},
        }

    def create(self, validated_data):
        user = XrideUser(
            username=validated_data['username'],
            email=validated_data['email'],
            wallet_balance=validated_data.get('wallet_balance', 0.00),
            phone_number=validated_data.get('phone_number'),
            address=validated_data.get('address'),
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

class CarSerializer(serializers.ModelSerializer):
    car_model = serializers.StringRelatedField()  # Assuming you want the car model's name
    location = serializers.StringRelatedField()  # Assuming you want the location name
    class Meta:
        model = Car
        fields = [
            'id', 'car_plate', 'door_status', 'temperature',
            'location_latitude', 'location_longitude', 'reservation_status',
            'booking_price_2H', 'booking_price_6H', 'booking_price_12H',
            'car_model', 'location'
        ]

class SimpleCarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Car
        fields = ['car_plate', 'car_model', 'location']  # Including car_plate, car_model, and location details

class SimplUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = XrideUser  # Ensure that XrideUser is correctly referenced, update if it's a different model
        fields = ['id', 'username']  # Include only id and username

class ReservationSerializer(serializers.ModelSerializer):
    car = SimpleCarSerializer()  # Nested serializer for car details
    user = SimplUserSerializer(read_only=True)  # Nested serializer for user details

    class Meta:
        model = Reservation
        fields = [
            'id',
            'user',  # Nested user details
            'car',  # Nested car details
            'start_time',
            'end_time',
            'reservation_plan',
            'status',
            'duration',  # Calculated duration
        ]

class ReservationHistorySerializer(serializers.ModelSerializer):
    reservation = ReservationSerializer()  # Nested reservation details
    car = SimpleCarSerializer()  # Nested car details
    user = SimplUserSerializer()  # Nested user details

    class Meta:
        model = ReservationHistory
        fields = [
            'id',
            'reservation',  # Nested reservation
            'car',  # Nested car details
            'user',  # Nested user details
            'start_time',
            'end_time',
            'reservation_plan',
            'status',
            'duration',
        ]

class CurrentlUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = XrideUser
        fields = ['username', 'email', 'first_name', 'last_name', 'wallet_balance', 'phone_number', 'address', 'national_id', 'personal_photo', 'licence_photo', 'national_id_photo']







class PaymentSerializer(serializers.ModelSerializer):
    user = SimplUserSerializer(read_only=True)  # Include the user serializer as read-only

    class Meta:
        model = Payment
        fields = [
            'id', 
            'user', 
            'transaction_id', 
            'order_id', 
            'collector', 
            'card_type', 
            'card_last_four', 
            'currency', 
            'amount', 
            'created_at', 
            'txn_response_code', 
            'status'
        ]

# class CarSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Car
#         fields = [
#             'id', 'car_name', 'car_plate', 'year', 
#             'door_status', 'temperature', 'location_latitude', 
#             'location_longitude', 'reservation_status', 
#             'booking_price_2H', 'booking_price_6H', 
#             'booking_price_12H'
#         ]

# class SimpleCarSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Car
#         fields = ['car_name', 'year']  # Include only car_name and year

# class SimplUserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = XrideUser
#         fields = ['id', 'username']  # Include only id and username

# class ReservationSerializer(serializers.ModelSerializer):
#     car = SimpleCarSerializer()  # Nested serializer for car details
#     user = SimplUserSerializer(read_only=True)  # Nested serializer for user details

#     class Meta:
#         model = Reservation
#         fields = [
#             'id',
#             'user',  # Nested user details
#             'car',  # Nested car details
#             'start_time',
#             'end_time',
#             'reservation_plan',
#             'status',
#             'duration',  # Calculated duration
#         ]
        