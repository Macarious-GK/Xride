from django.urls import path, include
from .views import *


urlpatterns = [    
    path('car/nearby-available/', AvailableCarsWithinRadiusView.as_view(), name='available_cars'),
    path('car/<int:car_id>/reserve/', ReserveCarView.as_view(), name='reserve_car'),
    path('car/<int:car_id>/release/', ReleaseCarView.as_view(), name='release_car'),
    path('car/<int:car_id>/status/', CarStatusView.as_view(), name='car-status'),
    path('car/<int:car_id>/update-door/', DoorStatusUpdateView.as_view(), name='update-door-status'),
    # #-----------------------------------------------------------
    path('user/profile/', UserDetailView.as_view(), name='view-profile'),
    path('user/trips/', UserListReservationsView.as_view(), name='release_car'),
    # path('user/<int:car_id>/payments/', TemperatureUpdateView.as_view(), name='update-temperature'),
    # #---------------------------------------------------------------------
    path('eco/', EchoView.as_view(), name='update-temperature'),


]