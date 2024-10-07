# iotapp/urls.py
from django.urls import path
from .views import *

urlpatterns = [
    path('car/<int:car_id>/status/', CarStatusView.as_view(), name='car-status'),
    path('car/<int:car_id>/update-door/', DoorStatusUpdateView.as_view(), name='update-door-status'),
    path('car/<int:car_id>/update-temperature/', TemperatureUpdateView.as_view(), name='update-temperature'),
    path('car/<int:car_id>/update-gas/', GasUpdateView.as_view(), name='update-gas'),
]