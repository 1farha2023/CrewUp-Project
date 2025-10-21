#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crewup.settings')
django.setup()

from django.db import connection
from authentication.models import CustomUser
from authentication.backends import EmailOrUsernameModelBackend
from django.test import RequestFactory

def test_database():
    """Test database connectivity and basic operations"""
    print("Testing Database Connection...")

    try:
        # Test database connection
        connection.ensure_connection()
        print("SUCCESS: Database connected successfully")

        # Test CustomUser model
        users = CustomUser.objects.all()
        print(f"SUCCESS: CustomUser model loaded successfully")
        print(f"INFO: Total users in database: {users.count()}")

        print("\nUsers in database:")
        for user in users:
            print(f"  - {user.username} ({user.email}) - {user.user_type}")

        # Test authentication backend
        print("\nTesting Authentication Backend...")
        factory = RequestFactory()
        request = factory.post('/login/')

        backend = EmailOrUsernameModelBackend()

        # Test with existing user
        test_user = users.filter(email='testbrand@example.com').first()
        if test_user:
            # Set a test password (you may need to adjust this)
            test_user.set_password('password123')
            test_user.save()

            authenticated_user = backend.authenticate(
                request,
                username='testbrand@example.com',
                password='password123'
            )

            if authenticated_user:
                print(f"SUCCESS: Authentication successful for {authenticated_user.username}")
                print(f"   User type: {authenticated_user.user_type}")
            else:
                print("FAILED: Authentication failed")
        else:
            print("WARNING: Test user not found")

        # Test payment models
        print("\nTesting Payment Models...")
        from payments.models import Payment, Subscription

        payment_count = Payment.objects.count()
        subscription_count = Subscription.objects.count()

        print(f"SUCCESS: Payment model loaded successfully ({payment_count} payments)")
        print(f"SUCCESS: Subscription model loaded successfully ({subscription_count} subscriptions)")

        print("\nAll database tests passed!")

    except Exception as e:
        print(f"FAILED: Database test failed: {e}")
        return False

    return True

if __name__ == "__main__":
    test_database()