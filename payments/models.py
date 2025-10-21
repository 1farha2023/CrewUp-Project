from django.db import models
from django.conf import settings
from django.utils import timezone


class Payment(models.Model):
    """Model to track individual payments/transactions"""

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payments')
    stripe_payment_intent_id = models.CharField(max_length=255, blank=True, null=True)
    stripe_checkout_session_id = models.CharField(max_length=255, blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='usd')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    description = models.TextField(blank=True, null=True)

    # Plan information
    plan_name = models.CharField(max_length=100, blank=True, null=True)
    plan_type = models.CharField(max_length=50, choices=[
        ('basic', 'Basic Plan'),
        ('pro', 'Pro Plan'),
        ('enterprise', 'Enterprise Plan'),
    ], blank=True, null=True)

    # Billing information
    is_subscription = models.BooleanField(default=False)
    billing_cycle = models.CharField(max_length=20, choices=[
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    ], blank=True, null=True)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.plan_name} - ${self.amount}"


class Subscription(models.Model):
    """Model to track user subscriptions"""

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('cancelled', 'Cancelled'),
        ('past_due', 'Past Due'),
        ('incomplete', 'Incomplete'),
        ('trialing', 'Trialing'),
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='subscription')
    stripe_subscription_id = models.CharField(max_length=255, unique=True)
    stripe_customer_id = models.CharField(max_length=255, blank=True, null=True)

    plan_name = models.CharField(max_length=100)
    plan_type = models.CharField(max_length=50, choices=[
        ('basic', 'Basic Plan'),
        ('pro', 'Pro Plan'),
        ('enterprise', 'Enterprise Plan'),
    ])

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    current_period_start = models.DateTimeField(blank=True, null=True)
    current_period_end = models.DateTimeField(blank=True, null=True)
    cancel_at_period_end = models.BooleanField(default=False)

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='usd')
    billing_cycle = models.CharField(max_length=20, choices=[
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    ])

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.plan_name} ({self.status})"

    @property
    def is_active(self):
        return self.status == 'active'

    @property
    def days_until_expiry(self):
        if self.current_period_end:
            return (self.current_period_end - timezone.now()).days
        return None
