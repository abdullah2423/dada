from django.shortcuts import render, redirect  # Add redirect if needed
from .forms import PaymentForm, SubscriptionForm
from .models import Payment ,Order, Subscription
import requests
import json
import os
from dotenv import load_dotenv
from django.http import HttpResponseBadRequest ,JsonResponse 
from .utils import get_card_token, create_subscription_with_payzaty

def payment_form(request):
    load_dotenv()

def payment_form(request):
    load_dotenv()

    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            order = form.save()

            # Construct Payzaty API request payload
            payload = {
                "merchant_id": os.environ.get('AccountNo'), 
                "api_key": os.environ.get('SecretKey'), 
                "order_id": order.order_id,
                "amount": order.amount, 
                "payment_methods": [method.name for method in order.payment_methods.all()],
                "card_types": [card.name for card in order.card_types.all()],
                "currency": order.currency,
                "language": order.language,
                "reference": order.reference,
                "customer": {
                    "name": order.customer.name,
                    "email": order.customer.email,
                    "phone": order.customer_phone,  # Corrected field name
                },
                "tokenization": True,
                "subscription": {"interval": "monthly", "end_date": "2025-03-31"},
                "response_url": order.response_url,
                "cancel_url": order.cancel_url,
                "payouts": [
                    {
                        "bank_code": order.bank_code,
                        "beneficiary_name": order.beneficiary_name,  # Corrected field name
                        "iban_number": order.iban_number,
                        "amount": order.amount,
                        "value_date": order.value_date,
                    }
                ],
            }

            # Send request to Payzaty checkout API
            headers = {
                "Content-Type": "application/json",
                "X-AccountNo": os.environ.get('AccountNo'),
                "X-SecretKey": os.environ.get('SecretKey')
            }
            response = requests.post('https://api.sandbox.payzaty.com/checkout', data=json.dumps(payload), headers=headers)

            # Handle Payzaty's response
            if response.status_code == 200:
                # Payment request successful
                payment_data = response.json()
                # Redirect to Payzaty's checkout page
                return redirect(payment_data['checkout_url'])
            elif response.status_code == 401:
                # Authentication failed
                return render(request, 'payment_error.html', context={'error_message': 'Authentication failed. Please check your merchant ID and API key.'})
            elif response.status_code == 422:
                # Invalid data was sent
                error_data = response.json()
                return render(request, 'payment_error.html', context={'error_message': f"Invalid data: {error_data.get('error_text')}"})
            elif response.status_code == 403:
                # Forbidden
                return render(request, 'payment_error.html', context={'error_message': 'Forbidden: Unsubscribed service.'})
            else:
                # Unexpected error
                return render(request, 'payment_error.html', context={'error_message': 'An unexpected error occurred with Payzaty. Please try again later.'})

    else:
        form = PaymentForm()
    
    return render(request, 'payment_form.html', {'form': form})
def get_checkout_details(checkout_id):
    base_url = "https://api.sandbox.payzaty.com"  # Update if production URL is different
    endpoint = f"/checkout/{checkout_id}"
    url = base_url + endpoint

    headers = {
        "Content-Type": "application/json",
        "X-AccountNo": os.environ.get('PAYZATY_MERCHANT_ID'),
        "X-SecretKey": os.environ.get('PAYZATY_API_KEY') 
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        checkout_data = response.json()
        return checkout_data  # Return the entire checkout data
    
    elif response.status_code == 401:
        return "Authentication Failed"  # Or raise a specific AuthenticationError 
    
    elif response.status_code == 404:
        return "Checkout does not exist"  # Or raise a CheckoutNotFoundError
    
    else:
        return "Unexpected Error"  # Replace with more specific handling later

def check_payment_status(request):
    checkout_id = request.GET.get('checkout_id')  # Retrieve the stored checkout_id 
    result = get_checkout_details(checkout_id)
    
    if isinstance(result, str):  # Indicates an error occurred
        if result == "Authentication Failed":
            return render(request, 'payment_error.html', context={'error_message': 'Authentication failed. Please check your merchant ID and API key.'})
        elif result == "Checkout does not exist":
            return render(request, 'payment_error.html', context={'error_message': 'Invalid checkout ID.'}) 
        else:  # Unexpected error
            return render(request, 'payment_error.html', context={'error_message': 'An unexpected error occurred with Payzaty. Please try again later.'})
    else:
        checkout_data = result  # Assuming 'result' is the parsed JSON
        status = checkout_data.get('status', 'Unknown') 

        if status == "Paid":
            # Update order status to 'paid'
            order = Order.objects.get(checkout_id=checkout_id)  
            order.status = 'paid'
            order.save()
            return render(request, 'payment_success.html') 
        elif status == "Pending":
            return render(request, 'payment_pending.html') 
        elif status == "Failed":
            # Handle payment failure, potentially updating order status
            return render(request, 'payment_error.html', context={'error_message': 'Payment failed.'})  
        else:  
            return render(request, 'payment_error.html', context={'error_message': 'Unknown payment status.'})

def process_subscription_payment(subscription_id):
    # ... Call the /subscription/{subscription_id}/pay endpoint 

    response = requests.post(...)  
    if response.status_code == 200:
        payload = response.json()
        if payload.get('status') == "Captured":  # Or the exact text they use
            subscription = Subscription.objects.get(pk=subscription_id)
            order = Order.objects.create(
                subscription=subscription,
                amount=payload['amount'],
                # ... other order details
            )
            # ... success logic, emails etc.
        else:  # 'Not Captured' or other unexpected status
            # ... Handle potential issues with the subscription payment
            pass  # Add error handling or retry logic here 

    elif response.status_code == 401:
        # Handle authentication errors
        pass
    elif response.status_code == 404:
        # Handle invalid subscription ID 
        pass
    elif response.status_code == 422:
        # Handle invalid input data 
        pass
    elif response.status_code == 403:
        # Handle forbidden (unsubscribed)
        pass
    else:
        # Handle other unexpected server errors
        pass  
 # In views.py


def process_token_payment(request):
    # Check if the request method is POST
    if request.method != 'POST':
        return HttpResponseBadRequest("Invalid request method.")

    # Validate and extract data from the request
    amount = request.POST.get('amount')
    currency = request.POST.get('currency')
    token = request.POST.get('token')
    reference = request.POST.get('reference')
    customer_name = request.POST.get('customer_name')
    customer_email = request.POST.get('customer_email')
    customer_phone = request.POST.get('customer_phone')
    response_url = request.POST.get('response_url')

    # Validate required fields
    if not all([amount, currency, token, reference, customer_name, customer_email, customer_phone, response_url]):
        return HttpResponseBadRequest("Missing required fields.")

    # Construct payload
    payload = {
        "amount": amount,
        "currency": currency,
        "payment_method": "Token",
        "token": token,
        "reference": reference,
        "customer": {
            "name": customer_name,
            "email": customer_email,
            "phone": customer_phone
        },
        "response_url": response_url
    }

    try:
        # Make the payment request
        response = requests.post('https://api.sandbox.payzaty.com/checkout/pay', json=payload, headers={
            "Content-Type": "application/json",
            "Authorization": os.environ.get('SecretKey')
        })
        response_data = response.json()

        # Handle different response scenarios
        if response.status_code == 200:
            checkout_id = response_data.get('checkout_id')
            authentication_url = response_data.get('authentication_url')
            return JsonResponse({"checkout_id": checkout_id, "authentication_url": authentication_url})
        elif response.status_code == 401:
            return HttpResponseBadRequest("Authentication Failed")
        elif response.status_code == 422:
            error_text = response_data.get('error_text', 'Invalid data was sent')
            return HttpResponseBadRequest(f"Invalid data: {error_text}")
        elif response.status_code == 404:
            return HttpResponseBadRequest("Token does not exist")
        elif response.status_code == 403:
            return HttpResponseBadRequest("Forbidden")
        else:
            return HttpResponseBadRequest("Unexpected Error")
    except Exception as e:
        return HttpResponseBadRequest(f"Error processing payment: {e}")

def create_subscription_with_payzaty(plan, card_token):
    # Define the endpoint URL for subscription creation
    subscription_creation_url = "https://api.payzaty.com/subscription/create"

    # Prepare the payload for the subscription creation request
    payload = {
        "plan": plan,
        "card_token": card_token
    }

    # Make the POST request to create the subscription
    try:
        response = requests.post(subscription_creation_url, json=payload)
        response.raise_for_status()  # Raise an exception for HTTP errors (e.g., 4xx or 5xx)
        subscription_data = response.json()
        subscription_id = subscription_data.get('subscription_id')
        return subscription_id
    except requests.exceptions.RequestException as e:
        # Handle exceptions that occur during the request
        print("Error creating subscription:", e)
        return None

def subscribe_view(request):
    if request.method == 'POST':
        form = SubscriptionForm(request.POST)
        if form.is_valid():
            # Get form data
            plan = form.cleaned_data['plan']
            card_data = {
                'card_number': request.POST.get('card_number'),
                'expiry_date': request.POST.get('expiry_date'),
                'cvv': request.POST.get('cvv')
            }
            
            # Tokenize card data securely
            card_token = get_card_token(card_data)
            if card_token:
                # Call Payzaty's subscription creation API
                subscription_id = create_subscription_with_payzaty(plan, card_token)
                
                # Create Subscription object (assuming Subscription model exists)
                subscription = Subscription.objects.create(plan=plan, subscription_id=subscription_id)
                
                # Redirect to success page
                return redirect('subscription_success')
            else:
                # Handle tokenization error
                return render(request, 'subscription_error.html', {'error_message': 'Error tokenizing card data'})
    else:
        form = SubscriptionForm()
    return render(request, 'subscribe.html', {'form': form})


def process_payment(request):
    # Check if the request method is POST
    if request.method != 'POST':
        return HttpResponseBadRequest("Invalid request method.")

    # Validate and extract data from the request
    amount = request.POST.get('amount')
    currency = request.POST.get('currency')
    token = request.POST.get('token')
    reference = request.POST.get('reference')
    customer_name = request.POST.get('customer_name')
    customer_email = request.POST.get('customer_email')
    customer_phone = request.POST.get('customer_phone')
    response_url = request.POST.get('response_url')

    # Validate required fields
    if not all([amount, currency, token, reference, customer_name, customer_email, customer_phone, response_url]):
        return HttpResponseBadRequest("Missing required fields.")

    # Construct payload
    payload = {
        "amount": amount,
        "currency": currency,
        "payment_method": "Token",
        "token": token,
        "reference": reference,
        "customer": {
            "name": customer_name,
            "email": customer_email,
            "phone": customer_phone
        },
        "response_url": response_url
    }

    try:
        # Make the payment request
        response = requests.post('https://api.sandbox.payzaty.com/checkout/pay', json=payload)
        response_data = response.json()

        # Handle different response scenarios
        if response.status_code == 200:
            checkout_id = response_data.get('checkout_id')
            authentication_url = response_data.get('authentication_url')
            return JsonResponse({"checkout_id": checkout_id, "authentication_url": authentication_url})
        elif response.status_code == 401:
            return HttpResponseBadRequest("Authentication Failed")
        elif response.status_code == 422:
            error_text = response_data.get('error_text', 'Invalid data was sent')
            return HttpResponseBadRequest(f"Invalid data: {error_text}")
        elif response.status_code == 403:
            return HttpResponseBadRequest("Forbidden")
        else:
            return HttpResponseBadRequest("Unexpected Error")
    except Exception as e:
        return HttpResponseBadRequest(f"Error processing payment: {e}")
def cancel_subscription(request, subscription_id): 
    headers = {
    "Content-Type": "application/json",
    "Authorization":os.environ.get('SecretKey'),  # Add any authorization token if required
}
    if request.method != 'POST':
        return HttpResponseBadRequest("Invalid request method.") 

    # ... (Authentication/authorization logic if applicable) ... 

    try:
        subscription = Subscription.objects.get(pk=subscription_id)
    except Subscription.DoesNotExist:
         return HttpResponseBadRequest("Subscription does not exist.")

    # Construct the request to Payzaty's cancel endpoint
    cancel_url = f"https://api.sandbox.payzaty.com/subscription/{subscription_id}/cancel"
    response = requests.post(cancel_url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        if data.get('success') == True:  # Check Payzaty's success indicator
            subscription.status = 'canceled' 
            subscription.save()
            return render(request, 'subscription_cancelled.html')  # Success!
        else:
            # Handle the case where Payzaty reports an error despite a 200 status
            return render(request, 'subscription_error.html', context={'error_message': 'An error occurred while cancelling the subscription.'})

    elif response.status_code == 400:
        error_data = response.json()
        if error_data.get('error_text') == "The subscription is already cancelled":
            # Display a message that the subscription was already cancelled
            return render(request, 'subscription_already_cancelled.html') 
        else:
            return render(request, 'subscription_error.html', context={'error_message': f"Invalid data: {error_data.get('error_text')}"})

    # ... Handle other error codes (401, etc.)

from django.http import JsonResponse, HttpResponseBadRequest

def full_refund(request, checkout_id):
    headers = {
        "Content-Type": "application/json",
        "Authorization": os.environ.get('SecretKey')
    }

    # Construct the request to Payzaty's full refund endpoint
    refund_url = f"https://api.sandbox.payzaty.com/checkout/{checkout_id}/refund"
    response = requests.post(refund_url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        if data.get('success', False):
            # Update your Order status for the refunded checkout_id
            return render(request, 'refund_success.html')  # Success!
        else:
            return render(request, 'refund_error.html', context={'error_message': data.get('msg', 'An unknown error occurred during the refund process.')})
    elif response.status_code == 401:
        return render(request, 'refund_error.html', context={'error_message': 'Authentication failed'})
    elif response.status_code == 404:
        return render(request, 'refund_error.html', context={'error_message': 'Checkout ID not found'})
    else:
        return render(request, 'refund_error.html', context={'error_message': 'An unexpected error occurred during the refund process.'})

def partial_refund(request, checkout_id):
    headers = {
        "Content-Type": "application/json",
        "Authorization": os.environ.get('SecretKey')
    }

    # Ensure the request method is POST
    if request.method != 'POST':
        return HttpResponseBadRequest("Invalid request method.")

    # Extract payload from the request
    payload = request.POST 

    # Construct the request to Payzaty's partial refund endpoint
    refund_url = f"https://api.sandbox.payzaty.com/checkout/{checkout_id}/refund/partial"
    response = requests.post(refund_url, json=payload, headers=headers)

    if response.status_code == 200:
        data = response.json()
        if data.get('success', False):
            # Update your Order status for the refunded checkout_id
            return render(request, 'refund_success.html')  # Success!
        else:
            return render(request, 'refund_error.html', context={'error_message': data.get('msg', 'An unknown error occurred during the refund process.')})
    elif response.status_code == 401:
        return render(request, 'refund_error.html', context={'error_message': 'Authentication failed'})
    elif response.status_code == 404:
        return render(request, 'refund_error.html', context={'error_message': 'Checkout ID not found'})
    else:
        return render(request, 'refund_error.html', context={'error_message': 'An unexpected error occurred during the refund process.'})
def check_card(request, bin):
    headers = {
        "Content-Type": "application/json",
        "Authorization": os.environ.get('SecretKey')  # Add any authorization token if required
    }

    if request.method != 'POST':
        return HttpResponseBadRequest("Invalid request method.")

    # Construct the request to Payzaty's check card endpoint
    check_url = f"https://api.sandbox.payzaty.com/card/check/{bin}"
    response = requests.post(check_url, headers=headers)

    if response.status_code == 200:
        return JsonResponse(response.json())  # Return Payzaty's response directly
    elif response.status_code == 401:
        return JsonResponse({'error': 'Authentication failed'}, status=401)
    elif response.status_code == 422:
        error_data = response.json()
        return JsonResponse({'error': f"Invalid data: {error_data.get('error_text')}"}, status=422)
    elif response.status_code == 404:
        return JsonResponse({'error': 'Card not found'}, status=404)
    else:
        return JsonResponse({'error': 'An unexpected error occurred'}, status=500)
import hashlib

def secure_hash_function(card_number, expiry_date, cvv):
    # Concatenate card data into a single string
    card_data = f"{card_number}-{expiry_date}-{cvv}"

    # Hash the concatenated card data using a secure hashing algorithm (e.g., SHA-256)
    hashed_data = hashlib.sha256(card_data.encode()).hexdigest()

    return hashed_data

def get_card_token(card_data):
    try:
        # Simulated tokenization process (replace this with your actual implementation)
        card_number = card_data.get('card_number')
        expiry_date = card_data.get('expiry_date')
        cvv = card_data.get('cvv')

        # Apply a secure tokenization method (e.g., hashing) to the card details
        hashed_token = secure_hash_function(card_number, expiry_date, cvv)
        return hashed_token
    except Exception as e:
        # Handle any errors that occur during tokenization
        print("Error tokenizing card:", e)
        return None
