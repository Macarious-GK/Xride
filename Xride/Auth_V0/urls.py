from django.urls import path
from .views import *
from . import views

urlpatterns = [
    path('activate/<str:uid>/<str:token>/', ActivateUser.as_view({'get': 'activation'}), name='activation'),
    #--------------------------------------------------------------------- Activation_Email
    path('user/delete-photo/', UserPhotoDeleteView.as_view(), name='user-photo-delete'),
    path('user/upload-photo/', UserPhotoUploadView.as_view(), name='user-photo-upload'),
    # #--------------------------------------------------------------------- User_Photo
    ]