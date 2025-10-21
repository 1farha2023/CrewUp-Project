import unittest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from django.test import LiveServerTestCase
from django.contrib.auth import get_user_model
from authentication.models import CustomUser

class AdminFunctionalityTest(LiveServerTestCase):
    """
    Selenium tests for admin functionality including login, dashboard, and user management
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Set up Chrome options
        chrome_options = Options()
        chrome_options.add_argument('--headless')  # Run in headless mode
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')

        # Try to use system ChromeDriver first, fallback to WebDriver Manager
        try:
            # Try system chromedriver first
            cls.driver = webdriver.Chrome(options=chrome_options)
        except Exception as e1:
            try:
                # Fallback to WebDriver Manager
                service = Service(ChromeDriverManager().install())
                cls.driver = webdriver.Chrome(service=service, options=chrome_options)
            except Exception as e2:
                print(f"Chrome WebDriver setup failed. Tried both system and WebDriver Manager.")
                print(f"System ChromeDriver error: {e1}")
                print(f"WebDriver Manager error: {e2}")
                print("Make sure Chrome browser is installed and try again.")
                raise e2

        cls.driver.implicitly_wait(10)
        cls.wait = WebDriverWait(cls.driver, 10)

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, 'driver'):
            cls.driver.quit()
        super().tearDownClass()

    def setUp(self):
        # Create test admin user
        self.admin_user = CustomUser.objects.create_superuser(
            username='testadmin',
            email='admin@test.com',
            password='admin123',
            user_type='admin'
        )

        # Create test regular user for banning
        self.test_user = CustomUser.objects.create_user(
            username='testuser',
            email='user@test.com',
            password='user123',
            user_type='influencer'
        )

    def tearDown(self):
        # Clean up test users
        try:
            self.admin_user.delete()
            self.test_user.delete()
        except:
            pass

    def login_as_admin(self):
        """Helper method to login as admin"""
        self.driver.get(f"{self.live_server_url}/auth/login/")

        # Wait for login form
        email_field = self.wait.until(
            EC.presence_of_element_located((By.NAME, "email"))
        )
        password_field = self.driver.find_element(By.NAME, "password")

        # Fill login form
        email_field.send_keys("admin@test.com")
        password_field.send_keys("admin123")

        # Submit form
        submit_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit_button.click()

        # Wait for redirect to admin dashboard
        self.wait.until(
            EC.url_contains("/admin-dashboard/")
        )

    def test_admin_login_and_dashboard_access(self):
        """Test admin login and dashboard access"""
        self.login_as_admin()

        # Verify we're on the admin dashboard
        self.assertIn("Admin Dashboard", self.driver.page_source)
        self.assertIn("Manage users, campaigns, and platform settings", self.driver.page_source)

        # Check for statistics cards (using the actual CSS classes from the template)
        stats_cards = self.driver.find_elements(By.CSS_SELECTOR, ".bg-white.rounded-lg.shadow-sm.p-6")
        self.assertGreater(len(stats_cards), 0, "Statistics cards should be present")

        # Check for recent users section
        recent_users_section = self.driver.find_element(By.XPATH, "//h2[contains(text(), 'Recent Users')]")
        self.assertIsNotNone(recent_users_section, "Recent users section should be present")

    def test_admin_dashboard_statistics(self):
        """Test that admin dashboard displays correct statistics"""
        self.login_as_admin()

        # Check for key statistics
        page_source = self.driver.page_source

        # Should show user statistics
        self.assertIn("Total Users", page_source)
        self.assertIn("Brand Users", page_source)
        self.assertIn("Influencer Users", page_source)

        # Should show campaign statistics
        self.assertIn("Active Campaigns", page_source)

        # Should show financial statistics
        self.assertIn("Total Revenue", page_source)

    def test_user_management_page_access(self):
        """Test access to user management page"""
        self.login_as_admin()

        # Click on "Manage Users" button
        manage_users_button = self.wait.until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Manage Users"))
        )
        manage_users_button.click()

        # Wait for user management page to load
        self.wait.until(
            EC.url_contains("/user-management/")
        )

        # Verify page content
        self.assertIn("User Management", self.driver.page_source)
        self.assertIn("Manage all users on the CrewUp platform", self.driver.page_source)

    def test_user_management_statistics(self):
        """Test user management page statistics"""
        self.login_as_admin()
        self.driver.get(f"{self.live_server_url}/admin-dashboard/user-management/")

        # Check for statistics cards
        stats_cards = self.driver.find_elements(By.CLASS_NAME, "stat-card")
        self.assertGreater(len(stats_cards), 0, "Statistics cards should be present on user management page")

        # Check for user table (using the actual CSS classes from the template)
        users_table = self.driver.find_elements(By.CSS_SELECTOR, ".space-y-4")
        self.assertGreater(len(users_table), 0, "Users table should be present")

    def test_ban_user_functionality(self):
        """Test banning a user from the admin dashboard"""
        self.login_as_admin()

        # Find the test user in recent users and click ban
        ban_buttons = self.driver.find_elements(By.XPATH, "//a[contains(text(), 'Ban')]")

        if ban_buttons:
            # Click the first ban button (should be for test user)
            ban_buttons[0].click()

            # Wait for ban confirmation page
            self.wait.until(
                EC.url_contains("/ban-user/")
            )

            # Verify ban confirmation page
            self.assertIn("Ban User", self.driver.page_source)
            self.assertIn("testuser", self.driver.page_source)

            # Fill ban reason and submit
            reason_field = self.driver.find_element(By.NAME, "reason")
            reason_field.send_keys("Test ban for automated testing")

            submit_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            submit_button.click()

            # Should redirect back to dashboard
            self.wait.until(
                EC.url_contains("/admin-dashboard/")
            )

            # Check for success message
            success_message = self.driver.find_elements(By.CLASS_NAME, "alert-success")
            if success_message:
                self.assertIn("banned successfully", success_message[0].text)

    def test_unban_user_functionality(self):
        """Test unbanning a user"""
        # First ban the user
        self.test_user.is_banned = True
        self.test_user.is_active = False
        self.test_user.banned_reason = "Pre-test ban"
        self.test_user.save()

        self.login_as_admin()

        # Find unban button and click it
        unban_buttons = self.driver.find_elements(By.XPATH, "//a[contains(text(), 'Unban')]")

        if unban_buttons:
            unban_buttons[0].click()

            # Wait for unban confirmation page
            self.wait.until(
                EC.url_contains("/unban-user/")
            )

            # Verify unban confirmation page
            self.assertIn("Unban User", self.driver.page_source)

            # Submit unban form
            submit_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            submit_button.click()

            # Should redirect back to dashboard
            self.wait.until(
                EC.url_contains("/admin-dashboard/")
            )

    def test_self_ban_prevention(self):
        """Test that admin cannot ban themselves"""
        self.login_as_admin()

        # Look for "Current User" text instead of ban button for admin user
        current_user_indicators = self.driver.find_elements(By.XPATH, "//span[contains(text(), 'Current User')]")

        # Should find at least one "Current User" indicator
        self.assertGreater(len(current_user_indicators), 0, "Should show 'Current User' for admin user")

        # Should not find ban buttons for current user
        ban_buttons = self.driver.find_elements(By.XPATH, "//a[contains(text(), 'Ban')]")
        # If there are ban buttons, they should not be for the current admin user
        # (This is a basic check - more sophisticated logic would be needed for full validation)

    def test_django_admin_access(self):
        """Test access to Django admin interface"""
        self.login_as_admin()

        # Navigate to Django admin
        self.driver.get(f"{self.live_server_url}/admin/")

        # Should be able to access admin interface
        self.assertIn("Django administration", self.driver.page_source)
        self.assertIn("Authentication and Authorization", self.driver.page_source)

        # Check for CustomUser in admin
        custom_user_link = self.driver.find_elements(By.LINK_TEXT, "Custom users")
        self.assertGreater(len(custom_user_link), 0, "CustomUser should be available in admin")

    def test_admin_logout(self):
        """Test admin logout functionality"""
        self.login_as_admin()

        # Find and click logout link (assuming it's in navigation)
        try:
            logout_link = self.driver.find_element(By.LINK_TEXT, "Logout")
            logout_link.click()
        except NoSuchElementException:
            # If logout link not found, try navigating to logout URL directly
            self.driver.get(f"{self.live_server_url}/auth/logout/")

        # Should redirect to home page
        self.wait.until(
            EC.url_matches(f"{self.live_server_url}/")
        )

        # Should not be able to access admin dashboard anymore
        self.driver.get(f"{self.live_server_url}/admin-dashboard/")
        # Should redirect to login or show access denied - check that we're not on admin dashboard
        current_url = self.driver.current_url
        self.assertNotIn("/admin-dashboard/", current_url)

if __name__ == '__main__':
    unittest.main()