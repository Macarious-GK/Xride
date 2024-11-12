from djoser.views import UserViewSet
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.template.response import TemplateResponse
from rest_framework.permissions import IsAuthenticated
from .serializers import *
from .utils import Manage_S3_Media  

from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model
from rest_framework.exceptions import AuthenticationFailed

class CustomTokenCreateView(TokenObtainPairView):
    """
    Custom view to handle the token creation response.
    If the user is registered but not activated, return a custom error message.
    If the user is not registered, return a "Wrong username or password" error message.
    """

    def post(self, request, *args, **kwargs):
        # Get the username and password from the request data
        username = request.data.get('username')
        password = request.data.get('password')

        # Check if the user exists
        try:
            user = get_user_model().objects.get(username=username)
        except get_user_model().DoesNotExist:
            # If user does not exist, return an error indicating incorrect username or password
            raise AuthenticationFailed("Wrong username or password")

        # Check if the user is active
        if not user.is_active:
            # If the user is not activated, return a custom error message
            return Response(
                {"detail": "Account is not activated. Please check your email for activation."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # If the user exists and is active, proceed with the normal token creation process
        return super().post(request, *args, **kwargs)

class ActivateUser(UserViewSet):
    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        kwargs.setdefault('context', self.get_serializer_context())
        
        # Inject uid and token into the serializer's data
        kwargs['data'] = {"uid": self.kwargs['uid'], "token": self.kwargs['token']}
        return serializer_class(*args, **kwargs)

    def activation(self, request, uid, token, *args, **kwargs):
        try:
            super().activation(request, *args, **kwargs)
            context = {
                "message": "Account successfully activated. You can now log in.",
                "message_class": "success"}
            return TemplateResponse(request, "activation_response.html", context, status=status.HTTP_200_OK)
        except Exception as e:
            context = {
                "message": "Activation failed. The link might be expired or invalid.",
                "message_class": "error",
                "detail": str(e),
                "suggestion": "Please request a new activation link or contact support if the problem persists."}
            return TemplateResponse(request, "activation_response.html", context, status=status.HTTP_400_BAD_REQUEST)

class UserPhotoDeleteView(APIView):
    def delete(self, request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        photo_type = request.data.get("photo_type")
        if photo_type not in ["personal_photo", "national_id_photo", "licence_photo"]:
            return Response({"error": "Invalid photo type."}, status=status.HTTP_400_BAD_REQUEST)
        file_field = getattr(user, photo_type, None)
        if not file_field or not file_field.name:
            return Response({"error": f"The {photo_type} for this User does not exist."}, status=status.HTTP_404_NOT_FOUND)

        file_name = file_field.name
        try:
            Manage_S3_Media(file_name,'delete')
        except Exception as e:
            return Response({"error": f"Failed to delete file from S3: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        setattr(user, photo_type, None)
        user.save()

        return Response({"message": f"{photo_type} deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

class UserPhotoUploadView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, *args, **kwargs):
        user = request.user
        photo_fields = ['personal_photo', 'national_id_photo', 'licence_photo']
        empty_fields = [field for field in photo_fields if not getattr(user, field)]
        populated_fields = [field for field in photo_fields if getattr(user, field)]
        data_to_upload = {field: request.data[field] for field in empty_fields if field in request.data}
        if not data_to_upload:
            return Response(
                {"error": "All photo fields are already populated. Please delete existing photos before uploading new ones."},
                status=status.HTTP_400_BAD_REQUEST)
        serializer = UserPhotoUploadSerializer(user, data=data_to_upload, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": f"Photos uploaded successfully for fields: {', '.join(data_to_upload.keys())}.",
                 "skipped": f"Already populated fields: {', '.join(populated_fields)}."},status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
