from django import forms
from .models import Order, Currency, Language, CardType, PaymentMethod, Subscription

class PaymentForm(forms.ModelForm):
    currency = forms.ChoiceField(choices=[(currency.pk, currency.name) for currency in Currency.objects.all()])
    language = forms.ChoiceField(choices=[(language.pk, language.name) for language in Language.objects.all()])
    payment_methods = forms.MultipleChoiceField(
        choices=PaymentMethod.PAYMENT_METHOD_CHOICES,
        widget=forms.CheckboxSelectMultiple()
    )
    card_types = forms.MultipleChoiceField(
        choices=CardType.CARD_TYPE_CHOICES,
        widget=forms.CheckboxSelectMultiple(),
        required=False  # Assuming card types might be optional depending on payment method
    )

    class Meta:
        model = Order
        fields = [
            'amount', 'customer_name', 'customer_email', 'customer_phone',
            'payment_methods', 'card_types', 'currency', 'reference', 'language', 
            'response_url', 'cancel_url'
        ]

class SubscriptionForm(forms.ModelForm):
    plan = forms.ChoiceField(choices=Subscription.PLAN_CHOICES) 
    # ... Potentially other fields for customer details

    class Meta:
        model = Subscription
        fields = ['plan']  # You might add more fields later
