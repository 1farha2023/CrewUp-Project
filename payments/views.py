import stripe
import json
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.utils import timezone
from decimal import Decimal

from .models import Payment, Subscription

# Initialize Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


@login_required
def create_checkout_session(request, plan_type, billing_cycle='monthly'):
    """Create a Stripe checkout session for the selected plan"""

    # Define plan pricing
    plan_prices = {
        'pro': {
            'monthly': 9900,  # $99.00 in cents
            'yearly': 59400,  # $594.00 in cents (50% discount)
        }
    }

    if plan_type not in plan_prices:
        messages.error(request, 'Invalid plan selected.')
        return redirect('pricing')

    try:
        # Get the price based on plan and billing cycle
        price = plan_prices[plan_type][billing_cycle]

        # Create checkout session
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': settings.PAYMENT_CURRENCY,
                    'product_data': {
                        'name': f'CrewUp {plan_type.title()} Plan ({billing_cycle})',
                        'description': f'Monthly subscription for {plan_type} plan' if billing_cycle == 'monthly' else f'Yearly subscription for {plan_type} plan',
                    },
                    'unit_amount': price,
                    'recurring': {
                        'interval': billing_cycle,
                    } if billing_cycle == 'monthly' else None,
                },
                'quantity': 1,
            }],
            mode='subscription' if billing_cycle == 'monthly' else 'payment',
            success_url=settings.PAYMENT_SUCCESS_URL + f'?session_id={{CHECKOUT_SESSION_ID}}&plan={plan_type}&cycle={billing_cycle}',
            cancel_url=settings.PAYMENT_CANCEL_URL,
            customer_email=request.user.email,
            metadata={
                'user_id': request.user.id,
                'plan_type': plan_type,
                'billing_cycle': billing_cycle,
            }
        )

        # Create payment record
        payment = Payment.objects.create(
            user=request.user,
            stripe_checkout_session_id=checkout_session.id,
            amount=price / 100,  # Convert from cents to dollars
            currency=settings.PAYMENT_CURRENCY,
            plan_name=f'{plan_type.title()} Plan',
            plan_type=plan_type,
            billing_cycle=billing_cycle,
            is_subscription=(billing_cycle == 'monthly'),
            status='pending'
        )

        return JsonResponse({
            'checkout_url': checkout_session.url,
            'session_id': checkout_session.id
        })

    except stripe.error.StripeError as e:
        messages.error(request, f'Payment error: {str(e)}')
        return JsonResponse({'error': str(e)}, status=400)
    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def payment_success(request):
    """Handle successful payment"""
    session_id = request.GET.get('session_id')
    plan_type = request.GET.get('plan')
    billing_cycle = request.GET.get('cycle', 'monthly')

    if not session_id:
        messages.error(request, 'Invalid payment session.')
        return redirect('pricing')

    try:
        # Retrieve session from Stripe
        session = stripe.checkout.Session.retrieve(session_id)

        # Update payment record
        payment = Payment.objects.filter(
            stripe_checkout_session_id=session_id,
            user=request.user
        ).first()

        if payment:
            payment.status = 'completed'
            payment.stripe_payment_intent_id = session.payment_intent
            payment.save()

            # Create or update subscription for recurring payments
            if billing_cycle == 'monthly' and session.mode == 'subscription':
                subscription, created = Subscription.objects.get_or_create(
                    user=request.user,
                    defaults={
                        'stripe_subscription_id': session.subscription,
                        'plan_name': payment.plan_name,
                        'plan_type': payment.plan_type,
                        'status': 'active',
                        'amount': payment.amount,
                        'currency': payment.currency,
                        'billing_cycle': payment.billing_cycle,
                    }
                )

                if not created:
                    subscription.stripe_subscription_id = session.subscription
                    subscription.status = 'active'
                    subscription.save()

            messages.success(request, f'Successfully subscribed to {payment.plan_name}!')
        else:
            messages.warning(request, 'Payment completed but no payment record found.')

        return render(request, 'payments/success.html', {
            'payment': payment,
            'plan_type': plan_type,
            'billing_cycle': billing_cycle,
        })

    except stripe.error.StripeError as e:
        messages.error(request, f'Payment verification error: {str(e)}')
        return redirect('pricing')
    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')
        return redirect('pricing')


@login_required
def payment_cancel(request):
    """Handle cancelled payment"""
    messages.info(request, 'Payment was cancelled.')
    return render(request, 'payments/cancel.html')


@csrf_exempt
@require_POST
def stripe_webhook(request):
    """Handle Stripe webhooks"""
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        return HttpResponse(status=400)

    # Handle the event
    if event['type'] == 'checkout.session.completed':
        handle_checkout_session_completed(event['data']['object'])
    elif event['type'] == 'invoice.payment_succeeded':
        handle_invoice_payment_succeeded(event['data']['object'])
    elif event['type'] == 'invoice.payment_failed':
        handle_invoice_payment_failed(event['data']['object'])
    elif event['type'] == 'customer.subscription.deleted':
        handle_subscription_deleted(event['data']['object'])

    return HttpResponse(status=200)


def handle_checkout_session_completed(session):
    """Handle successful checkout session"""
    try:
        payment = Payment.objects.filter(
            stripe_checkout_session_id=session['id']
        ).first()

        if payment:
            payment.status = 'completed'
            payment.stripe_payment_intent_id = session.get('payment_intent')
            payment.save()

            # Create subscription if this is a subscription payment
            if session.get('mode') == 'subscription':
                Subscription.objects.create(
                    user_id=payment.user_id,
                    stripe_subscription_id=session.get('subscription'),
                    stripe_customer_id=session.get('customer'),
                    plan_name=payment.plan_name,
                    plan_type=payment.plan_type,
                    status='active',
                    amount=payment.amount,
                    currency=payment.currency,
                    billing_cycle=payment.billing_cycle,
                    current_period_start=timezone.now(),
                    current_period_end=timezone.now() + timezone.timedelta(days=30 if payment.billing_cycle == 'monthly' else 365),
                )

    except Exception as e:
        print(f"Error handling checkout session completed: {e}")


def handle_invoice_payment_succeeded(invoice):
    """Handle successful subscription payment"""
    try:
        subscription = Subscription.objects.filter(
            stripe_subscription_id=invoice['subscription']
        ).first()

        if subscription:
            subscription.status = 'active'
            subscription.current_period_start = timezone.datetime.fromtimestamp(
                invoice['lines']['data'][0]['period']['start']
            )
            subscription.current_period_end = timezone.datetime.fromtimestamp(
                invoice['lines']['data'][0]['period']['end']
            )
            subscription.save()

    except Exception as e:
        print(f"Error handling invoice payment succeeded: {e}")


def handle_invoice_payment_failed(invoice):
    """Handle failed subscription payment"""
    try:
        subscription = Subscription.objects.filter(
            stripe_subscription_id=invoice['subscription']
        ).first()

        if subscription:
            subscription.status = 'past_due'
            subscription.save()

    except Exception as e:
        print(f"Error handling invoice payment failed: {e}")


def handle_subscription_deleted(subscription_data):
    """Handle cancelled subscription"""
    try:
        subscription = Subscription.objects.filter(
            stripe_subscription_id=subscription_data['id']
        ).first()

        if subscription:
            subscription.status = 'cancelled'
            subscription.cancel_at_period_end = False
            subscription.save()

    except Exception as e:
        print(f"Error handling subscription deleted: {e}")
