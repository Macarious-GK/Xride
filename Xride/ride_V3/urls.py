from django.urls import path, include
from .views import *


urlpatterns = [    
    path('car/nearby-available/', AvailableCarsWithinRadiusView.as_view(), name='available_cars'),
    path('car/<int:car_id>/reserve/', ReserveCarView.as_view(), name='reserve_car'),
    path('car/<int:car_id>/release/', ReleaseCarView.as_view(), name='release_car'),
    path('car/<int:car_id>/status/', CarStatusView.as_view(), name='car-status'),
    path('car/<int:car_id>/update-door/', DoorStatusUpdateView.as_view(), name='update-door-status'),
    # #--------------------------------------------------------------------- Car
    path('locations/parking/', ListLocatioView.as_view(), name='view-locations'),
    path('fines/', ListFineView.as_view(), name='view-fines'), 
    path('review/',PostReviewView.as_view(), name='post-review'),

    # #--------------------------------------------------------------------- location & fine & review
    path('user/profile/', UserDetailView.as_view(), name='view-profile'),
    path('user/trips/', UserListReservationsView.as_view(), name='release_car'),
    path('user/trips/active/', CheckActiveReservationView.as_view(), name='active-reservation'),

    # #--------------------------------------------------------------------- S3
    path('user/payments/create/', PaymentCreateView.as_view(), name='create-payment'),
    path('user/payments/confirm/', PaymentConfirmation.as_view(), name='confirm-payment'),
    path('user/payments-HMAC/confirm/', PaymentConfirmationWithHMAC.as_view(), name='confirm-payment-HMAC'),
    # #--------------------------------------------------------------------- Payment
    
    path('eco/', EchoView.as_view(), name='update-temperature'),


]