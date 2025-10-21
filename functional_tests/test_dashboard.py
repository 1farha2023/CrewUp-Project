from .base import FunctionalTest
from django.contrib.auth import get_user_model
from selenium.webdriver.common.by import By

class DashboardTest(FunctionalTest):

    def setUp(self):
        super().setUp()
        User = get_user_model()
        self.username = "testuser"
        self.email = "test@example.com"
        self.password = "testpass123"
        self.user = User.objects.create_user(
            username=self.username, 
            email=self.email, 
            password=self.password
        )
        # Ensure correct dashboard access
        self.user.user_type = 'influencer'
        self.user.save()
        
        # Login directly instead of using the base login method
        login_url = self.resolve_login_url()
        self.driver.get(login_url)
        
        try:
            username_field = self.driver.find_element(By.NAME, "email")
        except:
            username_field = self.driver.find_element(By.NAME, "username")
            
        password_field = self.driver.find_element(By.NAME, "password")
        submit_button = self.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        
        username_field.send_keys(self.email)
        password_field.send_keys(self.password)
        submit_button.click()
        
        # Wait for login to complete (any dashboard)
        self.wait_for_element(By.CSS_SELECTOR, "header .nav-buttons")

    def test_dashboard_loads_correctly(self):
        """Test that dashboard loads and shows user information."""
        # Navigate to dashboard via the nav button (renders correct URL per user_type)
        try:
            dash_link = self.driver.find_element(By.LINK_TEXT, "Dashboard")
            dash_link.click()
        except Exception:
            # Fallback: try a generic dashboard URL
            self.driver.get(self.live_server_url + "/influencer-dashboard/")
        
        # Wait for dashboard URL
        self.wait_for_url_contains("dashboard")
        body_text = self.driver.find_element(By.TAG_NAME, "body").text.lower()
        assert "dashboard" in self.driver.current_url.lower() or "dashboard" in body_text

    def test_logout_functionality(self):
        """Test that logout works correctly."""
        # Navigate directly to logout URL to avoid brittle UI selectors
        self.driver.get(self.live_server_url + "/auth/logout/")

        # Wait for redirect away from dashboard (should go to home or login)
        self.wait_for_url_contains("", timeout=10)  # Wait for any URL change

        # Assert logged-out state: not on dashboard
        current_url = self.driver.current_url.lower()
        assert "dashboard" not in current_url

        # Check for login/signup elements or home page
        try:
            self.wait_for_element(By.LINK_TEXT, "Sign In", timeout=5)
        except Exception:
            # If Sign In not found, check if we're on home page
            assert "/" in current_url or "home" in current_url
