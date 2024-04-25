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
    code = models.CharField(max_length=3, unique=True)  
    name = models.CharField(max_length=50)  

class Language(models.Model):
    code = models.CharField(max_length=5, unique=True)   
    name = models.CharField(max_length=50)  

class Order(models.Model):
    order_id = models.AutoField(primary_key=True)  
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    STATUS_CHOICES = [
        ('pending', 'Pending'), 
        ('success', 'Success'), 
        ('failed', 'Failed')
    ]
    status = models.CharField(max_length=50, choices=STATUS_CHOICES)
    customer_name = models.CharField(max_length=100)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=30)
    payment_methods = models.ManyToManyField(PaymentMethod)
    card_types = models.ManyToManyField(CardType)
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT)  
    reference = models.CharField(max_length=100, unique=True) 
    language = models.ForeignKey(Language, on_delete=models.PROTECT) 
    response_url = models.URLField()  # Added parentheses to make these method calls
    cancel_url = models.URLField()

class Payout(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed'),
    )
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
    recipient_bank_code = models.CharField(max_length=50)  
    recipient_name = models.CharField(max_length=100)
    iban = models.CharField(max_length=50) 
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    value_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payzaty_reference_id = models.CharField(max_length=100, null=True, blank=True)

class Subscription(models.Model):
    subscription_id = models.CharField(max_length=100, unique=True)
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    plan = models.CharField(max_length=50, blank=True)
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('canceled', 'Canceled')
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(null=True, blank=True)
    next_payment_date = models.DateTimeField() 
