from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *


urlpatterns = [    
    path('cars/nearby-available/', AvailableCarsWithinRadiusView.as_view(), name='available_cars'),
    path('car/<int:car_id>/release/', ReleaseCarView.as_view(), name='release_car'),
    path('car/<int:car_id>/reserve/', ReserveCarView.as_view(), name='reserve_car'),
    path('car/<int:car_id>/door-status/', ChangeDoorStatusView.as_view(), name='change_door_status'),

]