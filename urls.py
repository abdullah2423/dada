from django.urls import path, include
from django.contrib import admin
from .views import your_success_view, your_failure_view, subscribe_view ,cancel_subscription ,payment_form
from django.urls import path
from . import views

urlpatterns = [
    path('subscribe/', views.subscribe_view, name='subscribe'),  # Subscription view
    path('payment/', views.payment_form, name='payment'),  # Payment view
    path('process_payment/', views.process_payment, name='process_payment'),  # Payment processing endpoint
    path('check_payment_status/', views.check_payment_status, name='check_payment_status'),  # Payment status check endpoint
    path('cancel_subscription/<int:subscription_id>/', views.cancel_subscription, name='cancel_subscription'),  # Subscription cancellation endpoint
    path('full_refund/<int:checkout_id>/', views.full_refund, name='full_refund'),  # Full refund endpoint
    path('partial_refund/<int:checkout_id>/', views.partial_refund, name='partial_refund'),  # Partial refund endpoint
    path('check_card/<str:bin>/', views.check_card, name='check_card'),  # Card check endpoint
]
