from django.test import TestCase
from unittest.mock import patch
from payments.views import process_payment
from .models import Order

@patch('requests.post')  # Mock the 'requests.post' call for Payzaty
def test_payment_success(self, mock_post):
    # 1. Set up Test Data
    test_order = Order.objects.create(amount=100)  # Assuming you have an Order model

    # 2. Mock Payzaty Response
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {
        'checkout_id': 'test_checkout_id', 
        'status': 'Paid' 
    }  

    # 3. Simulate Request to Your View
    response = self.client.post('/process-payment/', {
        'order_id': test_order.id,
        # ... other necessary data...
    })

    # 4. Assertions
    self.assertEqual(response.status_code, 302)  # Expect a redirect after success 
    test_order.refresh_from_db() 
    self.assertEqual(test_order.status, 'paid') 
