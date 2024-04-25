from django.urls import path
from . import views
from django.contrib import admin
import include

urlpatterns = [
    path('admin/', admin.site.urls),  # Admin interface
    path('subscribe/', views.subscribe_view, name='subscribe'),  # Subscription view
    path('payment/', views.payment_form, name='payment_form'),  # Payment form view
    path('payment/status/', views.check_payment_status, name='check_payment_status'),  # Payment status check endpoint
    path('payment/subscription/', views.process_subscription_payment, name='process_subscription_payment'),  # Subscription payment processing endpoint
    path('payment/refund/full/<str:checkout_id>/', views.full_refund, name='full_refund'),  # Full refund endpoint
    path('payment/refund/partial/<str:checkout_id>/', views.partial_refund, name='partial_refund'),  # Partial refund endpoint
    path('payment/card/check/<str:bin>/', views.check_card, name='check_card'),  # Card check endpoint
    path('cancel_subscription/<int:subscription_id>/', views.cancel_subscription, name='cancel_subscription'),  # Subscription cancellation endpoint
    path('payments/', include('payments.urls')),  # Include URLs from 'payments' app
]