from django.db import models 
from django.conf import settings 


class PaymentMethod(models.Model):
    PAYMENT_METHOD_CHOICES = (
        ('CARD', 'Card'),
        ('APPLEPAY', 'ApplePay'),
        ('STCPAY', 'STCPay'),
    )
    name = models.CharField(max_length=50, choices=PAYMENT_METHOD_CHOICES)

class CardType(models.Model):
    CARD_TYPE_CHOICES = (
        ('MADA', 'Mada'),
        ('VISA', 'Visa'),
        ('MASTERCARD', 'MasterCard'),
    )
    name = models.CharField(max_length=50, choices=CARD_TYPE_CHOICES)
    
class Currency(models.Model):
    code = models.CharField(max_length=3, unique=True)  # e.g., "USD", "SAR"
    name = models.CharField(max_length=50)  # Optionally, a descriptive name

class Language(models.Model):
    code = models.CharField(max_length=5, unique=True)   # e.g., "en", "ar"
    name = models.CharField(max_length=50)  #  Optionally, a descriptive name

class Order(models.Model):
    order_id = models.AutoField(max_length=100, unique=True)  # Or AutoField
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50, choices=[
        ('pending', 'Pending'), 
        ('success', 'Success'), 
        ('failed', 'Failed')
    ])
    customer_name = models.CharField(max_length=100)
    customer_email = models.EmailField()
    customer_phone= models.CharField(max_length=30)
    payment_methods = models.ManyToManyField(PaymentMethod)
    card_types = models.ManyToManyField(CardType)
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT)  
    reference = models.CharField(max_length=100, unique=True) 
    language = models.ForeignKey(Language, on_delete=models.PROTECT) 
    response_url=models.URLField
    cancel_url=models.URLField
from django.db import models

class Payout(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed'),
    )
    order = models.ForeignKey('orders.Order', on_delete=models.SET_NULL, null=True)  # If payouts relate to orders
    recipient_bank_code = models.CharField(max_length=50)  # Adjust types if needed
    recipient_name = models.CharField(max_length=100)
    iban = models.CharField(max_length=50) 
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    value_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payzaty_reference_id = models.CharField(max_length=100, null=True, blank=True) # To store Payzaty's ID if they provide it
    

class Subscription(models.Model):
    subscription_id = models.CharField(max_length=100, unique=True)
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)   # Adjust 'User' to your User model 
    plan = models.CharField(max_length=50, blank=True)  # If you have multiple plans 
    status = models.CharField(max_length=20, choices=[('active', 'Active'), ('canceled', 'Canceled')]) 
    start_date = models.DateTimeField(auto_now_add=True)  
    end_date = models.DateTimeField(null=True, blank=True)  
    next_payment_date = models.DateTimeField() 
