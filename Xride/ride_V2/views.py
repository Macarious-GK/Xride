# iotapp/views.py
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Car
from .serializers import CarSerializer

class CarStatusView(APIView):
    """Get the current temperature and door status of the car."""
    
    def get(self, request, car_id):
        try:
            car = Car.objects.get(pk=car_id)
            serializer = CarSerializer(car)
            return Response(serializer.data)
        except Car.DoesNotExist:
            return Response({'error': 'Car not found'}, status=status.HTTP_404_NOT_FOUND)


class DoorStatusUpdateView(APIView):
    """Update the door status of the car."""
    
    def post(self, request, car_id):
        try:
            car = Car.objects.get(pk=car_id)
            action = request.data.get('action')

            if action in ['lock', 'unlock']:
                car.door_status = 'locked' if action == 'lock' else 'unlocked'
                car.save()
                return Response({'status': f'Door {action} command sent.'})

            return Response({'error': 'Invalid action'}, status=status.HTTP_400_BAD_REQUEST)
        except Car.DoesNotExist:
            return Response({'error': 'Car not found'}, status=status.HTTP_404_NOT_FOUND)


class TemperatureUpdateView(APIView):
    """Update the temperature of the car."""
    
    def post(self, request, car_id):
        try:
            car = Car.objects.get(pk=car_id)
            new_temperature = request.data.get('temperature')

            if new_temperature is not None:
                car.temp = new_temperature
                car.save()
                return Response({'status': 'Temperature updated successfully.', 'new_temperature': car.temp}, status=status.HTTP_200_OK)

            return Response({'error': 'Temperature value is required.'}, status=status.HTTP_400_BAD_REQUEST)
        except Car.DoesNotExist:
            return Response({'error': 'Car not found'}, status=status.HTTP_404_NOT_FOUND)


class GasUpdateView(APIView):
    """Update the gas level of the car."""
    
    def post(self, request, car_id):
        try:
            car = Car.objects.get(pk=car_id)
            new_gas = request.data.get('gas')

            if new_gas is not None:
                car.gas = new_gas
                car.save()
                return Response({'status': 'Gas updated successfully.', 'new_gas': car.gas}, status=status.HTTP_200_OK)

            return Response({'error': 'Gas value is required.'}, status=status.HTTP_400_BAD_REQUEST)
        except Car.DoesNotExist:
            return Response({'error': 'Car not found'}, status=status.HTTP_404_NOT_FOUND)
