from .base import FunctionalTest
from django.contrib.auth import get_user_model
from selenium.webdriver.common.by import By

class AuthenticationTest(FunctionalTest):

    def setUp(self):
        super().setUp()
        User = get_user_model()
        self.username = "testuser"
        self.email = "test@example.com"
        self.password = "testpass123"
        # Create user and assign to self.user
        self.user = User.objects.create_user(
            username=self.username,
            email=self.email,
            password=self.password
        )
        # Set user_type after creation
        self.user.user_type = 'influencer'
        self.user.save()

    def test_successful_login(self):
        """Test that a user can log in successfully."""
        # Use the actual login process
        login_url = self.resolve_login_url()
        self.driver.get(login_url)
        
        # Fill login form - adjust selectors based on your actual login form
        try:
            username_field = self.driver.find_element(By.NAME, "email")
        except Exception:
            username_field = self.driver.find_element(By.NAME, "username")
        
        password_field = self.driver.find_element(By.NAME, "password")
        submit_button = self.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        
        username_field.send_keys(self.email)
        password_field.send_keys(self.password)
        submit_button.click()
        
        # Wait for redirect and check success
        self.wait_for_url_contains("dashboard")
        assert "dashboard" in self.driver.current_url.lower()

    def test_invalid_login(self):
        """Test that invalid login shows appropriate error message."""
        login_url = self.resolve_login_url()
        self.driver.get(login_url)
        
        # Fill with invalid credentials
        try:
            username_field = self.driver.find_element(By.NAME, "email")
        except Exception:
            username_field = self.driver.find_element(By.NAME, "username")
            
        password_field = self.driver.find_element(By.NAME, "password")
        submit_button = self.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        
        username_field.send_keys("wronguser@gmail.com")
        password_field.send_keys("wrongpass")
        submit_button.click()
        
        # Check for error message - wait a bit for any error to appear
        import time
        time.sleep(2)
        
        body_text = self.driver.find_element(By.TAG_NAME, 'body').text
        error_found = any(word in body_text.lower() for word in ['invalid', 'error', 'incorrect', 'unable'])
        assert error_found, f"Expected error message not found. Page content: {body_text}"
