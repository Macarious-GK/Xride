import requests
from django.http import JsonResponse
from django.conf import settings
import hmac
import hashlib
import json

def generate_hmac(data):
    return hmac.new(settings.PAYMOB_HMAC_SECRET.encode(), data.encode(), hashlib.sha256).hexdigest()

def create_payment(request):
    if request.method == 'POST':
        amount = request.POST.get('amount')  # Get the amount from the request
        
        # Prepare the order payload
        order_data = {
            "amount_cents": int(amount) * 100,  # Amount in cents
            "currency": "EGP",  # Currency
            "merchant_id": settings.PAYMOB_MERCHANT_ID,
            "integration_id": settings.PAYMOB_INTEGRATION_ID,
            "description": "Payment Description",  # Add your payment description
        }

        # Generate HMAC
        hmac_value = generate_hmac(json.dumps(order_data))

        # Make a request to create the order
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {settings.PAYMOB_API_KEY}',
            'HMAC': hmac_value,
        }

        response = requests.post("https://accept.paymob.com/api/ecommerce/orders", json=order_data, headers=headers)

        return JsonResponse(response.json())
