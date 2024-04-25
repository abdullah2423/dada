from django.urls import path, include
from django.contrib import admin
from .views import your_success_view, your_failure_view, subscribe_view ,cancel_subscription ,payment_form
urlpatterns = [
     path('admin/', admin.site.urls),
     path('payments/', include('payments.urls')),  # Map to your 'payments' app
     path('success/', your_success_view, name='payment_success'),
    path('failure/', your_failure_view, name='payment_failure'),
    path('failure/', your_failure_view, name='payment_failure'),
    path('subscribe/', subscribe_view, name='subscribe'),
    path('', payment_form, name='payment_form'),
    path('cancel-subscription/<int:subscription_id>/', cancel_subscription, name='cancel_subscription'), # Add this line


    ]