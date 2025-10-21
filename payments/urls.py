from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    # Payment checkout
    path('create-checkout/<str:plan_type>/<str:billing_cycle>/', views.create_checkout_session, name='create_checkout_session'),

    # Payment results
    path('success/', views.payment_success, name='payment_success'),
    path('cancel/', views.payment_cancel, name='payment_cancel'),

    # Stripe webhooks
    path('webhook/', views.stripe_webhook, name='stripe_webhook'),
]