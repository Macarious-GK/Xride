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
    class Meta:
        model = Car
        fields = [
            'id', 'car_name', 'car_plate', 'year', 
            'door_status', 'temperature', 'location_latitude', 
            'location_longitude', 'reservation_status', 
            'booking_price_2H', 'booking_price_6H', 
            'booking_price_12H'
        ]

class SimpleCarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Car
        fields = ['car_name', 'year']  # Include only car_name and year
class SimplUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = XrideUser
        fields = ['username']  # Include only car_name and year


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
