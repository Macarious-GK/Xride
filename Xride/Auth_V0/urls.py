from django.urls import path
from .views import *
from . import views

urlpatterns = [
    path('activate/<str:uid>/<str:token>/', ActivateUserView.as_view(), name='activate-user'),
    path('password/reset/confirm/<str:uid>/<str:token>/', PasswordResetConfirmView.as_view(), name='password-user-reset'),
    ]