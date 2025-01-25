from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from ride_V3.models import User

class XrideUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'wallet_balance', 'phone_number', 'address', 'national_id', 'password']
        extra_kwargs = {
            'password': {'write_only': True},
            'groups': {'required': False},
            'user_permissions': {'required': False},
            'email': {'required': True},
            'national_id': {'required': True},
        }

    def validate(self, data):
        # Check if the username is unique (case-insensitive)
        if User.objects.filter(username__iexact=data['username']).exists():
            raise ValidationError({"username": "This username is already taken."})
        
        # Check if the email is unique
        if User.objects.filter(email=data['email']).exists():
            raise ValidationError({"email": "This email is already in use."})

        # Check if the national_id is unique
        if User.objects.filter(national_id=data['national_id']).exists():
            raise ValidationError({"national_id": "This national ID is already in use."})

        return data

    def create(self, validated_data):
        # Create user instance
        user = User(
            username=validated_data['username'],
            email=validated_data['email'],
            wallet_balance=validated_data.get('wallet_balance', 0.00),
            phone_number=validated_data.get('phone_number'),
            address=validated_data.get('address'),
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            national_id=validated_data.get('national_id', ''),
        )

        # Validate and set the password
        password = validated_data['password']
        validate_password(password, user)  # Optional password validation
        user.set_password(password)
        user.is_active = False  # Set to False initially if you want to verify later

        user.save()
        return user

class CurrentlUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'wallet_balance', 'phone_number', 'address', 'national_id', 'personal_photo', 'licence_photo', 'national_id_photo']

class UserPhotoUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['personal_photo', 'licence_photo', 'national_id_photo']
        
    def validate(self, data):
        if not any(field in data for field in ['personal_photo', 'licence_photo', 'national_id_photo']):
            raise serializers.ValidationError("No photo type specified.")
        return data

