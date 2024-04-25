from django import forms
from .models import Order, Currency ,Language ,CardType ,PaymentMethod
from django.forms import CheckboxSelectMultiple

class PaymentForm(forms.ModelForm):
    class Meta:
        currency = forms.ModelChoiceField(queryset=Currency.objects.all())
        Language = forms.ModelChoiceField(queryset=Language.objects.all())
        payment_methods = forms.MultipleChoiceField(
        choices=PaymentMethod.PAYMENT_METHOD_CHOICES,
        widget=CheckboxSelectMultiple()
    )

        card_types = forms.MultipleChoiceField(
        choices=CardType.CARD_TYPE_CHOICES,
        widget=CheckboxSelectMultiple(),
        required=False  # Assuming card types might be optional depending on payment method
    )
        model = Order
        fields = [
            'amount', 'customer_name', 'customer_email', 'customer_phone',
            'payment_methods', 'card_types', 'currency', 'reference', 'language', 
            'response_url', 'cancel_url'  # Include the new fields 
        ]
