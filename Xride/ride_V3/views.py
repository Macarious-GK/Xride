import hashlib
import hmac
from decimal import Decimal
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, BasePermission
from rest_framework import status
from django.db.models import F
from rest_framework import generics
from .models import *
from .serializers import *
from django.utils import timezone
from math import radians, cos, sin, asin, sqrt
from datetime import datetime
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.shortcuts import render
from .mqtt_subscriber_cloud import *
from django.core.cache import cache
from django.http import JsonResponse
import redis
# -------------------------------------Reusable views--------------------------------------------

def live(request):
    return render(request, 'notfy.html')

redis_client = redis.StrictRedis.from_url(
    "rediss://red-cjcsrendb61s739bj610:B59haYUZ3iFrOM9g0mzbWubr2ZfReoIc@oregon-redis.render.com:6379",
    ssl_cert_reqs=None  # Disables certificate validation
)

def test_redis(request):
    try:
        # Retrieve all car data from Redis
        car_keys = redis_client.keys("car:*")  # Get all keys matching "car:*"
        
        if not car_keys:
            return JsonResponse({"message": "No car data found in Redis."})
        
        # Fetch the data for each car
        cars = {}
        for key in car_keys:
            car_data = redis_client.get(key)
            if car_data:
                cars[key.decode()] = json.loads(car_data)

        return JsonResponse({"message": "✅ Retrieved all car data from Redis", "cars": cars})

    except Exception as e:
        return JsonResponse({"error": f"❌ Redis connection failed: {str(e)}"})
    
plans_map = {
    "2H": 2,
    "6H": 6,
    "12H": 12,
}

def calculate_duration_in_hours(start_time: datetime, end_time: datetime) -> float:
    duration = end_time - start_time  # Calculate duration as a timedelta
    duration_in_hours = duration.total_seconds() / 3600  # Convert seconds to hours
    return round(duration_in_hours,4)

def haversine(lon1, lat1, lon2, lat2):
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * asin(sqrt(a))
    r = 6371  # Earth radius in km
    return c * r

class HasActiveReservation(BasePermission):
    def has_permission(self, request, view):
        car_id = view.kwargs.get('car_id')
        return Reservation.objects.filter(user=request.user, car_id=car_id, status='active').exists()

# -------------------------------------Car list/reserve/release/status/update door views--------------------------------------------

class AvailableCarsWithinRadiusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        user_lat = request.query_params.get('latitude')
        user_lon = request.query_params.get('longitude')
        if  not user.verified:
            return Response({"error": "User Not Verified yet, please wait until your account is verified."}, status=status.HTTP_400_BAD_REQUEST)
        

        if not user_lat or not user_lon:
            return Response({'error': 'Please provide valid latitude and longitude.'}, status=status.HTTP_400_BAD_REQUEST)

        user_lat = float(user_lat)
        user_lon = float(user_lon)

        # Fetch cars with minimal data needed (no full object fetch)
        cars = Car.objects.filter(reservation_status='available').only('id', 'location_latitude', 'location_longitude')
        
        nearby_cars = [
            CarSerializer(car).data for car in cars
            if haversine(user_lon, user_lat,car.location_longitude,car.location_latitude ) <= 1000
        ]

        return Response({'nearby_cars': nearby_cars}, status=status.HTTP_200_OK)
    
class ReserveCarView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, car_id):
        user = request.user
        reservation_plan = request.data.get('reservation_plan')  # Expecting '2H', '6H', or '12H'
        user_lat = request.data.get('location_latitude')
        user_lon = request.data.get('location_longitude')

        if  not user.verified:
            return Response({"error": "User Not Verified yet, please wait until your account is verified."}, status=status.HTTP_400_BAD_REQUEST)
        
        if not user_lat or not user_lon:
            return Response({"error": "User location is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the car exists
        car = Car.objects.filter(id=car_id).first()
        if not car:
            return Response({"error": "Car not found."}, status=status.HTTP_404_NOT_FOUND)

        # Check if the user is within 50 meters of the car
        distance_car_user = haversine(float(user_lon), float(user_lat), car.location_longitude, car.location_latitude)
        distance_park_user = haversine(car.location.longitude, car.location.latitude, car.location_longitude, car.location_latitude)
        print(distance_car_user,distance_park_user)
        if distance_car_user > .2 or distance_park_user > car.location.radius:
            return Response({"error": "You are too far from the car or parking to reserve it."}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the user has an active reservation
        active_reservation = Reservation.objects.filter(user=user, status='active').first()
        if active_reservation:
            return Response({"error": "You already have an active reservation."}, status=status.HTTP_400_BAD_REQUEST)

        # Check car availability
        if car.reservation_status != 'available':
            return Response({"error": "Car is already reserved or unavailable."}, status=status.HTTP_400_BAD_REQUEST)

        # Determine the booking price based on the reservation plan
        booking_price_field = f"booking_price_{reservation_plan}"
        booking_price = getattr(car, booking_price_field, None)

        if booking_price is None:
            return Response({"error": "Invalid reservation plan."}, status=status.HTTP_400_BAD_REQUEST)

        if user.wallet_balance < booking_price:
            return Response({"error": "Insufficient account balance."}, status=status.HTTP_400_BAD_REQUEST)

        # Deduct the booking price from the user's wallet balance and create reservation
        with transaction.atomic():
            user.wallet_balance -= booking_price
            user.save(update_fields=['wallet_balance'])
            reservation = Reservation.objects.create(
                user=user,
                car=car,
                reservation_plan=reservation_plan,
                start_time=timezone.now(),
                reservation_Locatiion_Source= car.location
            )
            car.reservation_status = 'reserved'
            car.save(update_fields=['reservation_status'])

        return Response({
                'reservation_id': reservation.id,
                'car_id': reservation.car.id,
                'car_model': reservation.car.car_model.model_name,
                'car_plate': reservation.car.car_plate,
                'reservation_plan': reservation.reservation_plan,
                'start_time': reservation.start_time,
                'end_time': reservation.start_time + timezone.timedelta(hours=plans_map[reservation.reservation_plan]),
                'status': reservation.status,
            }, status=status.HTTP_200_OK)
    
class ReleaseCarView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, car_id):
        user = request.user
        reservation_park_dist = request.data.get('park_dist')
        user_lat = request.data.get('location_latitude')
        user_lon = request.data.get('location_longitude')

        if  not user.verified:
            return Response({"error": "User Not Verified yet, please wait until your account is verified."}, status=status.HTTP_400_BAD_REQUEST)
        

        reservation_park_dist_obj = get_object_or_404(Location, id=reservation_park_dist)

        if not reservation_park_dist :
            return Response({"error": "park_dist is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the car exists
        car = Car.objects.filter(id=car_id).first()
        if not car:
            return Response({"error": "Car not found."}, status=status.HTTP_404_NOT_FOUND)
        
        # if car.engine_status == 'on':
        #     return Response({"error": "Car engine is on, please turn it off before releasing the car."}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the car is reserved by the current user
        reservation = Reservation.objects.filter(user=user, car=car, status='active').first()
        if not reservation:
            return Response({"error": "You do not have a reservation for this car."}, status=status.HTTP_403_FORBIDDEN)
        
        distance = haversine(float(user_lon), float(user_lat), reservation_park_dist_obj.longitude, reservation_park_dist_obj.latitude)
        if distance > reservation_park_dist_obj.radius:
            return Response({"error": "You are too far from the parking"}, status=status.HTTP_400_BAD_REQUEST)
        
        
        distance_car_park = haversine(car.location_longitude, car.location_latitude, reservation_park_dist_obj.longitude, reservation_park_dist_obj.latitude)
        if distance_car_park > reservation_park_dist_obj.radius:
            return Response({"error": "Car is too far from the parking"}, status=status.HTTP_400_BAD_REQUEST)
        
        if car.door_status == 'unlocked':
            return Response({"error": "Car door is unlocked, please lock it before releasing the car."}, status=status.HTTP_400_BAD_REQUEST)

        # Set the reservation status to completed
        reservation.status = 'completed'
        reservation.end_time = timezone.now()  # Set the end time to now
        reservation.duration = self.calculate_duration_in_hours(reservation.start_time, reservation.end_time)
        reservation.save()
        # Create a record in ReservationHistory
        reservation_history = ReservationHistory.objects.create(
           reservation_ID = reservation.id,
            user=reservation.user,
            car=reservation.car,
            start_time=reservation.start_time,
            end_time=reservation.end_time,
            reservation_plan=reservation.reservation_plan,
            reservation_Locatiion_Source = reservation.reservation_Locatiion_Source,
            reservation_Locatiion_Distnation = reservation_park_dist_obj,
            status='completed',  # The status is completed for history
            duration=reservation.duration
        )
        

        # Delete the reservation after moving it to history
        reservation.delete()

        # Set the car status to available
        car.reservation_status = 'available'
        # car.location_latitude = user_lat
        # car.location_longitude = user_lon
        # car.door_status = 'locked'  # Lock the door when releasing the car
        car.location = reservation_park_dist_obj
        car.save(update_fields=['reservation_status','location'])

        return Response({
            "message": f"You have successfully released {car.car_model.model_name}.",
            "duration_hours": reservation_history.duration  # Return the duration from the history
        }, status=status.HTTP_200_OK)

    def calculate_duration_in_hours(self, start_time, end_time):
        duration = end_time - start_time
        return duration.total_seconds() / 3600  # Convert seconds to hours

class CarStatusView(APIView):
    permission_classes = [IsAuthenticated, HasActiveReservation]

    def get(self, request, car_id):
        user = request.user
        if  not user.verified:
            return Response({"error": "User Not Verified yet, please wait until your account is verified."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            car = Car.objects.get(pk=car_id)
            serializer = CarSerializer(car)
            status_TOPIC = f"car/{car_id}/xride/status"
            data = {"status":"status"}
            type = "status"
            # publish_message(status_TOPIC, data,type)
            return Response(serializer.data)
        except Car.DoesNotExist:
            return Response({'error': 'Car not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': 'An error occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DoorStatusUpdateView(APIView):
    permission_classes = [IsAuthenticated, HasActiveReservation]

    @transaction.atomic
    def post(self, request, car_id):
        user = request.user
        if  not user.verified:
            return Response({"error": "User Not Verified yet, please wait until your account is verified."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            car = Car.objects.select_for_update().get(pk=car_id)
            # Toggle door status
            new_status = 'locked' if car.door_status == 'unlocked' else 'unlocked'
            status_message = f"Door {new_status} successfully."
            car.door_status = new_status

            # publish_car_door_state(car_id, car.door_status)  # Publish updated status
            car.save()  # Save the updated status
            Door_TOPIC = f"car/{car_id}/xride/door"
            data = {"door":car.door_status}
            type = "door"
            # publish_message(Door_TOPIC, data,type)
            return Response({'status': status_message})
        except Car.DoesNotExist:
            return Response({'error': 'Car not found'}, status=status.HTTP_404_NOT_FOUND)

# -------------------------------------Reservation list review/ Location & Fines list/  views--------------------------------------------

class UserDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    queryset = User.objects.all()
    serializer_class = CurrentlUserSerializer

    def get_object(self):
        return self.request.user  # Return the current authenticated user
    
class CheckActiveReservationView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        active_reservation = Reservation.objects.filter(user=request.user, status='active').first()
        
        if active_reservation:
            data = {
                'has_active_reservation': True,
                'reservation_id': active_reservation.id,
                'car_id': active_reservation.car.id,
                'car_model': active_reservation.car.car_model.model_name,
                'car_plate': active_reservation.car.car_plate,
                'reservation_plan': active_reservation.reservation_plan,
                'start_time': active_reservation.start_time,
                'end_time': active_reservation.start_time + timezone.timedelta(hours=plans_map[active_reservation.reservation_plan]),
                'status': active_reservation.status,
            }
            return Response(data, status=status.HTTP_200_OK)
        else:
            return Response({'has_active_reservation': False}, status=status.HTTP_200_OK)

class UserListReservationsView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user = request.user
        if  not user.verified:
            return Response({"error": "User Not Verified yet, please wait until your account is verified."}, status=status.HTTP_400_BAD_REQUEST)
        
        reservations = ReservationHistory.objects.filter(user=user)
        serializer = ReservationHistorySerializer(reservations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class ListLocatioView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user = request.user
        if  not user.verified:
            return Response({"error": "User Not Verified yet, please wait until your account is verified."}, status=status.HTTP_400_BAD_REQUEST)
        
        locations = Location.objects.all()
        serializer = LocationSerializer(locations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class ListFineView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user = request.user
        if  not user.verified:
            return Response({"error": "User Not Verified yet, please wait until your account is verified."}, status=status.HTTP_400_BAD_REQUEST)
        
        fines = Fine.objects.filter(user=user)
        serializer = FineSerializer(fines, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class PostReviewView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        reservationHistory_id = request.data.get('reservation_id')
        rating = request.data.get('rating')
        review = request.data.get('review')

        if  not user.verified:
            return Response({"error": "User Not Verified yet, please wait until your account is verified."}, status=status.HTTP_400_BAD_REQUEST)
        
        if not reservationHistory_id :
            return Response({"error": "Reservation ID is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        ReservationHistory_obj = get_object_or_404(ReservationHistory, id=reservationHistory_id)

        if ReservationHistory_obj.user != user:
            return Response({"error": "You are not allowed to review this reservation."}, status=status.HTTP_403_FORBIDDEN)
        ReservationHistory_obj.review_rate = rating
        ReservationHistory_obj.review_text = review
        ReservationHistory_obj.save()

        return Response({"message": "Review added successfully."}, status=status.HTTP_200_OK)

# -------------------------------------Payment views--------------------------------------------
class EchoView(APIView):
    """Echoes back the POST request body as JSON."""
    permission_classes = [AllowAny]
    def post(self, request):
        # Get the request data
        data = request.data
        print(data)
        if not data:
            return Response({'error': "nothing"}, status=status.HTTP_200_OK)
        
        data = data["obj"]
        received_hmac = request.query_params.get('hmac')
        
         # Define the order of keys for HMAC calculation
        hmac_keys = [
            'amount_cents', 'created_at', 'currency', 'error_occured', 'has_parent_transaction', 'id',
            'integration_id', 'is_3d_secure', 'is_auth', 'is_capture', 'is_refunded', 'is_standalone_payment',
            'is_voided', 'order.id', 'owner', 'pending', 'source_data.pan', 'source_data.sub_type',
            'source_data.type', 'success'
        ]

        # Sort the data by key and concatenate the values in the specified order
        concatenated_string = self.generate_hmac_string(data, hmac_keys)

        print("concatenated_string",concatenated_string)

        # Calculate the HMAC using SHA512 and your HMAC secret
        secret = "D229E5A90A84B96B8ACAAD3ADF2BE93C"
        calculated_hmac = hmac.new(secret.encode(), concatenated_string.encode(), hashlib.sha512).hexdigest()

        print("calculated_hmac",calculated_hmac)
        print("received_hmac",received_hmac)
        # Compare the calculated HMAC with the received HMAC
        if calculated_hmac != received_hmac:
            return Response({'error': 'Invalid HMAC'}, status=status.HTTP_403_FORBIDDEN)

        print("HMAC is valid")
        # Return the data as the response
        return Response(data, status=status.HTTP_200_OK)
    
    def get_nested_value(self, data, key):
        keys = key.split('.')
        for k in keys:
            data = data.get(k, {})
        return data
    
    def generate_hmac_string(self, data, keys):
        hmac_string = ''
        for key in keys:
            value = self.get_nested_value(data, key)
            if value in (True, False):
                value = str(value).lower()
            hmac_string += str(value)
        return hmac_string

class PaymentCreateView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):
        amount = request.data.get('amount')
        order_id = request.data.get('order_id')
        user = request.user
        if  not user.verified:
            return Response({"error": "User Not Verified yet, please wait until your account is verified."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if amount is provided
        if not amount or not order_id:
            return Response({"error": "Amount and Order_id is required."}, status=status.HTTP_204_NO_CONTENT)

        # Check if the user has any pending payments
        # pending_payment = Payment.objects.filter(user=user, status='pending').first()
        pending_payment = False
        payment_order_exist = Payment.objects.filter(user=user, order_id=order_id).first()
        if pending_payment or payment_order_exist:
            return Response({"error": "You already have this order or a pending Payment"}, status=status.HTTP_204_NO_CONTENT)

        # Prepare data for the serializer
        data = {
            "amount": amount,
            "currency": "EGP",  # Assuming EGP is the default currency
            "status": "pending",  # Setting status to 'pending'
            "order_id": order_id
        }

        # Initialize the serializer with the data
        serializer = PaymentSerializer(data=data, context={'request': request})
        if serializer.is_valid():
            payment = serializer.save(user=user)  # Save the payment with the user
            response_data = {
                "id": payment.id,
                "amount": payment.amount,
                "currency": payment.currency,
                "status": payment.status,
                "created_at": payment.created_at.isoformat(),  # Return the created_at in ISO format
                "order_id": payment.order_id,
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
class PaymentConfirmation(APIView):

    def post(self, request):
        payment_type = request.data.get('type')
        obj = request.data.get('obj')
        if payment_type != "TRANSACTION" or not isinstance(obj, dict):
            return Response({"error": "Invalid request format."}, status=status.HTTP_400_BAD_REQUEST)

        # Extract required fields safely
        transaction_id = obj.get('id')
        order_data = obj.get('order', {})
        source_data = obj.get('source_data', {})
        data_info = obj.get('data', {})

        order_id = order_data.get('id')
        collector = order_data.get('merchant', {}).get('company_name')
        card_type = source_data.get('sub_type')
        card_last_four = source_data.get('pan')
        currency = obj.get('currency')
        amount = obj.get('amount_cents')
        txn_response_code = data_info.get('txn_response_code')
        status_info = data_info.get('migs_result')

        # Validate the extracted data
        required_fields = [transaction_id, order_id, card_type, currency, amount, txn_response_code, status_info]
        if any(field is None for field in required_fields):
            return Response({"error": "Missing required fields in the transaction data."}, status=status.HTTP_400_BAD_REQUEST)
        if Payment.objects.filter(transaction_id=transaction_id).exists():
            return Response({"error": "Transaction ID already exists."}, status=status.HTTP_400_BAD_REQUEST)
        # Find the payment record using the transaction ID and user
        payment = get_object_or_404(Payment, order_id=order_id, status="pending")

        # Validate amount and currency
        if payment.amount != amount or payment.currency != currency:
            return Response({"error": "Invalid transaction data."}, status=status.HTTP_400_BAD_REQUEST)

        # Update the payment record
        payment.order_id = order_id
        payment.collector = collector
        payment.card_type = card_type
        payment.card_last_four = card_last_four[-4:] if card_last_four else None  # Ensure only the last four digits are stored
        payment.currency = currency
        payment.amount = amount
        payment.txn_response_code = txn_response_code
        payment.status = status_info
        payment.transaction_id = transaction_id

        with transaction.atomic():
            payment.save()
            # Update the user's wallet balance
            user = payment.user
            user.wallet_balance += Decimal(amount) / Decimal(100)
            user.save()
        return Response({"message": "Payment record confirmed."}, status=status.HTTP_200_OK)

class PaymentConfirmationWithHMAC(APIView):
    permission_classes = [AllowAny]
    secret = "D229E5A90A84B96B8ACAAD3ADF2BE93C"
    hmac_keys = [
        'amount_cents', 'created_at', 'currency', 'error_occured', 'has_parent_transaction', 'id',
        'integration_id', 'is_3d_secure', 'is_auth', 'is_capture', 'is_refunded', 'is_standalone_payment',
        'is_voided', 'order.id', 'owner', 'pending', 'source_data.pan', 'source_data.sub_type',
        'source_data.type', 'success'
    ]

    def post(self, request):
        data = request.data.get("obj")
        if not data:
            return Response({'error': "No data provided."}, status=status.HTTP_400_BAD_REQUEST)

        received_hmac = request.query_params.get('hmac')
        if not self.validate_hmac(data, received_hmac):
            return Response({'error': 'Invalid HMAC'}, status=status.HTTP_403_FORBIDDEN)

        payment_type, obj = request.data.get('type'), request.data.get('obj')
        if not self.is_valid_transaction_request(payment_type, obj):
            return Response({"error": "Invalid request format."}, status=status.HTTP_400_BAD_REQUEST)

        transaction_data = self.extract_transaction_data(obj)
        if not self.validate_transaction_data(transaction_data):
            return Response({"error": "Missing required fields in the transaction data."}, status=status.HTTP_400_BAD_REQUEST)
        
        transaction_id = transaction_data['transaction_id']
        if Payment.objects.filter(transaction_id=transaction_id).exists():
            return Response({"error": "This Transaction already Completed."}, status=status.HTTP_400_BAD_REQUEST)
        order_id = transaction_data['order_id']
        payment = self.get_pending_payment(order_id)
        if not self.validate_payment_amount_currency(payment, transaction_data['amount'], transaction_data['currency']):
            return Response({"error": "Invalid transaction data."}, status=status.HTTP_400_BAD_REQUEST)

        try:
        # Wrap both operations inside an atomic transaction
            with transaction.atomic():
                # First operation: Update payment record
                self.update_payment_record(payment, transaction_data)

                # Second operation: Update user wallet balance
                self.update_user_wallet_balance(payment.user, transaction_data['amount'])
                return Response({"message": "Payment record confirmed."}, status=status.HTTP_200_OK)

        except Exception as e:
            # If an error occurs, the transaction is automatically rolled back
            print(f"An error occurred: {e}")
            return Response({"message": "Payment record confirmed."}, status=status.HTTP_402_PAYMENT_REQUIRED)

    def validate_hmac(self, data, received_hmac):
        concatenated_string = self.generate_hmac_string(data, self.hmac_keys)
        calculated_hmac = hmac.new(self.secret.encode(), concatenated_string.encode(), hashlib.sha512).hexdigest()
        return calculated_hmac == received_hmac

    def is_valid_transaction_request(self, payment_type, obj):
        return payment_type == "TRANSACTION" and isinstance(obj, dict)

    def extract_transaction_data(self, obj):
        return {
            'transaction_id': obj.get('id'),
            'order_id':  obj.get('payment_key_claims').get('billing_data').get('postal_code'),
            'collector': obj.get('order', {}).get('merchant', {}).get('company_name'),
            'card_type': obj.get('source_data', {}).get('sub_type'),
            'card_last_four': obj.get('source_data', {}).get('pan', '')[-4:],
            'currency': obj.get('currency'),
            'amount': obj.get('amount_cents') / 100,
            'txn_response_code': obj.get('data', {}).get('txn_response_code'),
            'status_info': obj.get('data', {}).get('migs_result')
        }

    def validate_transaction_data(self, transaction_data):
        required_fields = ['transaction_id', 'order_id', 'card_type', 'currency', 'amount', 'txn_response_code', 'status_info']
        return all(transaction_data.get(field) is not None for field in required_fields)

    def get_pending_payment(self, order_id):
        return get_object_or_404(Payment, order_id=order_id, status="pending")

    def validate_payment_amount_currency(self, payment, amount, currency):
        return payment.amount == amount and payment.currency == currency

    def update_payment_record(self, payment, transaction_data):
        payment.order_id = transaction_data['order_id']
        payment.collector = transaction_data['collector']
        payment.card_type = transaction_data['card_type']
        payment.card_last_four = transaction_data['card_last_four']
        payment.currency = transaction_data['currency']
        payment.amount = transaction_data['amount']
        payment.txn_response_code = transaction_data['txn_response_code']
        payment.status = transaction_data['status_info']
        payment.transaction_id = transaction_data['transaction_id']

        with transaction.atomic():
            payment.save()

    def update_user_wallet_balance(self, user, amount):
        user.wallet_balance += Decimal(amount)
        user.save()

    def get_nested_value(self, data, key):
        keys = key.split('.')
        for k in keys:
            data = data.get(k, {})
        return data

    def generate_hmac_string(self, data, keys):
        hmac_string = ''
        for key in keys:
            value = self.get_nested_value(data, key)
            value = str(value).lower() if isinstance(value, bool) else str(value)
            hmac_string += value
        return hmac_string
    
