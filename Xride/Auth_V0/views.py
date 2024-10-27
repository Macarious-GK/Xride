from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
import requests

class ActivateUserView(APIView):
    """
    This view handles the user account activation by sending a request 
    to Djoser's activation endpoint with the uid and token.
    """
    permission_classes = [AllowAny] 
    def get(self, request, uid, token):
        activation_url = "http://localhost:8000/auth/users/activation/"
        data = {
            'uid': uid,
            'token': token}
        try:
            response = requests.post(activation_url, json=data, timeout=10)
            response.raise_for_status()  # Raises an exception for 4xx or 5xx HTTP errors
        except requests.exceptions.RequestException as e:
            return Response({"detail": "Error activating the user. Please try again later."},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        if response.status_code == status.HTTP_204_NO_CONTENT:
            return Response({"detail": "User activated successfully."},status=status.HTTP_200_OK)
        return Response(
            {
                'detail': 'Activation failed. Please check the activation link or contact support.',
                'errors': response.json()},status=response.status_code)



class PasswordResetConfirmView(APIView):
    """
    This view handles the password reset confirmation by sending a request 
    to Djoser's password reset confirmation endpoint with the uid, token, and new password.
    """
    permission_classes = [AllowAny]

    def post(self, request, uid, token):
        # Get new passwords from request data
        new_password = request.data.get("new_password")
        re_new_password = request.data.get("re_new_password")
        if new_password != re_new_password:
            return Response(
                {"detail": "New passwords do not match."},status=status.HTTP_400_BAD_REQUEST)
        
        reset_confirm_url = "http://localhost:8000/auth/users/reset_password_confirm/"
        data = {
            'uid': uid,
            'token': token,
            'new_password': new_password,
            're_new_password': re_new_password
        }
        try:
            response = requests.post(reset_confirm_url, json=data, timeout=10)
            response.raise_for_status()  # Raises an exception for 4xx or 5xx HTTP errors
        except requests.exceptions.RequestException as e:
            print(f"Error: {str(e)}")  # You may want to log this instead of print in production
            return Response(
                {"detail": "Error resetting the password. Please try again later."},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        if response.status_code == status.HTTP_204_NO_CONTENT:
            return Response(
                {"detail": "Password reset successfully."},status=status.HTTP_200_OK)
        else:
            return Response(
                {
                    'detail': 'Password reset failed. Please check the reset link or contact support.',
                    'errors': response.json()  # Include Djoser response errors if available
                },status=response.status_code)
