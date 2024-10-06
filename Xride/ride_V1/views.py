from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.db.models import F
from .models import Car, Reservation
from .serializers import CarSerializer
from math import radians, cos, sin, asin, sqrt

# Haversine function (unchanged)
def haversine(lon1, lat1, lon2, lat2):
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * asin(sqrt(a))
    r = 6371  # Earth radius in km
    return c * r

# 1. Available Cars View
class AvailableCarsWithinRadiusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_lat = request.query_params.get('latitude')
        user_lon = request.query_params.get('longitude')

        if not user_lat or not user_lon:
            return Response({'error': 'Please provide valid latitude and longitude.'}, status=status.HTTP_400_BAD_REQUEST)

        user_lat = float(user_lat)
        user_lon = float(user_lon)

        # Fetch cars with minimal data needed (no full object fetch)
        cars = Car.objects.filter(status='available').only('id', 'latitude', 'longitude')
        
        nearby_cars = [
            CarSerializer(car).data for car in cars
            if haversine(user_lon, user_lat, car.longitude, car.latitude) <= 1.5
        ]

        return Response({'nearby_cars': nearby_cars}, status=status.HTTP_200_OK)


# 2. Reserve Car View
class ReserveCarView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, car_id):
        user = request.user

        # Check if the car exists
        car = Car.objects.filter(id=car_id).first()
        if not car:
            return Response({"error": "Car not found."}, status=status.HTTP_404_NOT_FOUND)

        # Check car availability and reservation in one go to avoid extra queries
        if car.status != 'available':
            return Response({"error": "Car is already reserved or unavailable."}, status=status.HTTP_400_BAD_REQUEST)

        if Reservation.objects.filter(user=user).exists():
            return Response({"error": "You already have a reserved car."}, status=status.HTTP_400_BAD_REQUEST)

        # Create reservation and update car status atomically
        Reservation.objects.create(user=user, car=car)
        car.status = 'reserved'
        car.save(update_fields=['status'])

        return Response({"message": f"You have successfully reserved {car.car_name}."}, status=status.HTTP_200_OK)


# 3. Release Car View
class ReleaseCarView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, car_id):
        user = request.user

        # Check if the car exists
        car = Car.objects.filter(id=car_id).first()
        if not car:
            return Response({"error": "Car not found."}, status=status.HTTP_404_NOT_FOUND)

        # Check if the car is reserved by the current user
        reservation = Reservation.objects.filter(user=user, car=car).first()
        if not reservation:
            return Response({"error": "You do not have permission to release this car."}, status=status.HTTP_403_FORBIDDEN)

        # Release the car: Delete the reservation
        reservation.delete()

        # Set the car status to available and the door status to close
        car.status = 'available'
        car.door_status = 'close'
        car.save(update_fields=['status', 'door_status'])  # Only update relevant fields

        return Response({"message": f"You have successfully released {car.car_name}."}, status=status.HTTP_200_OK)

# 4. Change Door Status View
class ChangeDoorStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, car_id):
        user = request.user

        # Check if the car exists
        car = Car.objects.filter(id=car_id).first()
        if not car:
            return Response({"error": "Car not found."}, status=status.HTTP_404_NOT_FOUND)

        # Check if the car is reserved by the user (single query to check)
        reservation = Reservation.objects.filter(user=user, car=car).first()
        if not reservation:
            return Response({"error": "You do not have permission to change the door status of this car."}, status=status.HTTP_403_FORBIDDEN)

        # Use `F()` expressions to directly toggle door status in the DB (without retrieving the entire object)
        car.door_status = 'close' if car.door_status == 'open' else 'open'
        car.save(update_fields=['door_status'])

        return Response({"message": f"The door is now {car.door_status}."}, status=status.HTTP_200_OK)




# import paho.mqtt.client as mqtt

# # Function to publish the door status via MQTT
# def publish_door_status(car_id, door_status):
#     client = mqtt.Client()
    
#     # Connect to the MQTT broker (replace with the actual IP of the broker)
#     client.connect("BROKER_IP", 1883, 60)
    
#     # Construct the topic specific to the car
#     topic = f"car/{car_id}/door_status"
    
#     # Publish the door status (open or close)
#     message = f"door_status:{door_status}"
#     client.publish(topic, message)
    
#     # Start the MQTT loop to handle communication (non-blocking)
#     client.loop_start()

# # The view to change the car's door status
# class ChangeDoorStatusView(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request, car_id):
#         user = request.user

#         # Check if the car exists
#         car = Car.objects.filter(id=car_id).first()
#         if not car:
#             return Response({"error": "Car not found."}, status=status.HTTP_404_NOT_FOUND)

#         # Check if the car is reserved by the user
#         reservation = Reservation.objects.filter(user=user, car=car).first()
#         if not reservation:
#             return Response({"error": "You do not have permission to change the door status of this car."}, status=status.HTTP_403_FORBIDDEN)

#         # Toggle the door status
#         new_door_status = 'close' if car.door_status == 'open' else 'open'
#         car.door_status = new_door_status
#         car.save(update_fields=['door_status'])

#         # Publish the updated door status to the IoT device (car)
#         publish_door_status(car_id, new_door_status)

#         return Response({"message": f"The door is now {car.door_status}."}, status=status.HTTP_200_OK)
