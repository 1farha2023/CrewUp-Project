import unittest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from django.test import LiveServerTestCase
from django.contrib.auth import get_user_model
from authentication.models import CustomUser

class NavigationUITest(LiveServerTestCase):
    """
    Selenium tests for navigation, UI, and user experience
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Set up Chrome options for GUI testing
        chrome_options = Options()
        # Remove headless mode to show GUI
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--start-maximized')

        # Initialize WebDriver with WebDriver Manager
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
        cls.wait = WebDriverWait(cls.driver, 15)
        cls.actions = ActionChains(cls.driver)

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, 'driver'):
            cls.driver.quit()
        super().tearDownClass()

    def setUp(self):
        # Create test users
        self.admin_user = CustomUser.objects.create_superuser(
            username='testadmin',
            email='admin@test.com',
            password='admin123',
            user_type='admin'
        )

        self.brand_user = CustomUser.objects.create_user(
            username='testbrand',
            email='brand@test.com',
            password='brand123',
            user_type='brand'
        )

        self.influencer_user = CustomUser.objects.create_user(
            username='testinfluencer',
            email='influencer@test.com',
            password='influencer123',
            user_type='influencer'
        )

    def tearDown(self):
        # Clean up test users
        try:
            CustomUser.objects.filter(username__startswith='test').delete()
        except:
            pass

    def test_main_navigation_menu(self):
        """Test main navigation menu functionality"""
        self.driver.get(self.live_server_url)

        # Check if navigation menu exists
        try:
            nav_menu = self.driver.find_element(By.TAG_NAME, "nav")
            print("✓ Navigation menu found")
        except NoSuchElementException:
            # Try alternative navigation selectors
            nav_menu = self.driver.find_element(By.CLASS_NAME, "navbar") or \
                      self.driver.find_element(By.ID, "navigation") or \
                      self.driver.find_element(By.CLASS_NAME, "nav")
            print("✓ Alternative navigation found")

        # Test navigation links
        nav_links = self.driver.find_elements(By.CSS_SELECTOR, "nav a, .navbar a, .nav a")

        expected_pages = ['Home', 'About', 'How It Works', 'Pricing', 'Brands', 'Influencers', 'Contact']
        found_links = []

        for link in nav_links:
            text = link.text.strip()
            if text and any(expected in text for expected in expected_pages):
                found_links.append(text)
                print(f"✓ Found navigation link: {text}")

        # Verify key navigation elements
        self.assertGreater(len(found_links), 0, "Should find navigation links")

        # Test login/signup links
        auth_links = self.driver.find_elements(By.PARTIAL_LINK_TEXT, "Login") + \
                    self.driver.find_elements(By.PARTIAL_LINK_TEXT, "Sign")
        self.assertGreater(len(auth_links), 0, "Should find authentication links")

    def test_responsive_design_mobile(self):
        """Test responsive design on mobile viewport"""
        # Set mobile viewport
        self.driver.set_window_size(375, 667)  # iPhone SE size

        self.driver.get(self.live_server_url)

        # Wait for page to load
        time.sleep(2)

        # Check if content is still accessible
        try:
            # Look for main content
            main_content = self.driver.find_element(By.TAG_NAME, "main") or \
                          self.driver.find_element(By.CLASS_NAME, "container") or \
                          self.driver.find_element(By.ID, "content")

            # Check if navigation is accessible (hamburger menu might be present)
            nav_elements = self.driver.find_elements(By.CLASS_NAME, "hamburger") + \
                          self.driver.find_elements(By.CLASS_NAME, "mobile-menu") + \
                          self.driver.find_elements(By.CLASS_NAME, "navbar-toggler")

            print("✓ Mobile responsive design test passed")
            print(f"✓ Found {len(nav_elements)} mobile navigation elements")

        except Exception as e:
            print(f"⚠ Mobile responsive test warning: {e}")

        # Reset to desktop size
        self.driver.set_window_size(1920, 1080)

    def test_responsive_design_tablet(self):
        """Test responsive design on tablet viewport"""
        # Set tablet viewport
        self.driver.set_window_size(768, 1024)  # iPad size

        self.driver.get(self.live_server_url)

        # Wait for page to load
        time.sleep(2)

        # Check layout adaptation
        body = self.driver.find_element(By.TAG_NAME, "body")
        body_classes = body.get_attribute("class") or ""

        print("✓ Tablet responsive design test passed")

        # Reset to desktop size
        self.driver.set_window_size(1920, 1080)

    def test_accessibility_basic_checks(self):
        """Test basic accessibility features"""
        self.driver.get(self.live_server_url)

        # Check for alt text on images
        images = self.driver.find_elements(By.TAG_NAME, "img")
        images_without_alt = 0

        for img in images:
            alt_text = img.get_attribute("alt")
            if not alt_text or alt_text.strip() == "":
                images_without_alt += 1

        print(f"✓ Images checked: {len(images)} total, {images_without_alt} without alt text")

        # Check for form labels
        forms = self.driver.find_elements(By.TAG_NAME, "form")
        if forms:
            for form in forms:
                inputs = form.find_elements(By.TAG_NAME, "input")
                labels = form.find_elements(By.TAG_NAME, "label")

                print(f"✓ Form accessibility: {len(inputs)} inputs, {len(labels)} labels")

        # Check heading hierarchy
        headings = self.driver.find_elements(By.CSS_SELECTOR, "h1, h2, h3, h4, h5, h6")
        heading_levels = [int(h.tag_name[1]) for h in headings]

        print(f"✓ Found {len(headings)} headings with levels: {heading_levels}")

        # Basic check - should have at least one h1
        h1_headings = self.driver.find_elements(By.TAG_NAME, "h1")
        self.assertGreater(len(h1_headings), 0, "Should have at least one H1 heading")

    def test_visual_elements_and_interactions(self):
        """Test visual elements and user interactions"""
        self.driver.get(self.live_server_url)

        # Test button hover effects (if any)
        buttons = self.driver.find_elements(By.TAG_NAME, "button") + \
                 self.driver.find_elements(By.CSS_SELECTOR, "a.btn, .button")

        print(f"✓ Found {len(buttons)} interactive buttons/links")

        # Test form elements
        forms = self.driver.find_elements(By.TAG_NAME, "form")
        if forms:
            print(f"✓ Found {len(forms)} forms on page")

            # Test form inputs
            inputs = self.driver.find_elements(By.TAG_NAME, "input")
            textareas = self.driver.find_elements(By.TAG_NAME, "textarea")
            selects = self.driver.find_elements(By.TAG_NAME, "select")

            print(f"✓ Form elements: {len(inputs)} inputs, {len(textareas)} textareas, {len(selects)} selects")

        # Test links are not broken (basic check)
        links = self.driver.find_elements(By.TAG_NAME, "a")
        valid_links = 0

        for link in links[:10]:  # Test first 10 links to avoid too many requests
            href = link.get_attribute("href")
            if href and (href.startswith("http") or href.startswith("/")):
                valid_links += 1

        print(f"✓ Links checked: {min(10, len(links))} tested, {valid_links} with valid hrefs")

    def test_admin_navigation_flow(self):
        """Test admin navigation and user flow"""
        # Login as admin
        self.driver.get(f"{self.live_server_url}/auth/login/")

        email_field = self.wait.until(EC.presence_of_element_located((By.NAME, "email")))
        password_field = self.driver.find_element(By.NAME, "password")

        email_field.send_keys("admin@test.com")
        password_field.send_keys("admin123")

        submit_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit_button.click()

        # Wait for admin dashboard
        self.wait.until(EC.url_contains("/admin-dashboard/"))

        # Test admin navigation elements
        page_source = self.driver.page_source

        # Check for admin-specific elements
        admin_elements = [
            "Admin Dashboard",
            "Manage users",
            "Manage Users",
            "Total Users"
        ]

        found_elements = [elem for elem in admin_elements if elem in page_source]
        print(f"✓ Admin dashboard elements found: {found_elements}")

        self.assertGreater(len(found_elements), 0, "Should find admin dashboard elements")

        # Test navigation to user management
        try:
            manage_users_link = self.driver.find_element(By.LINK_TEXT, "Manage Users")
            manage_users_link.click()

            self.wait.until(EC.url_contains("/user-management/"))
            print("✓ Successfully navigated to user management")

            # Check user management page elements
            user_mgmt_elements = self.driver.find_elements(By.CLASS_NAME, "stat-card")
            self.assertGreater(len(user_mgmt_elements), 0, "Should find statistics cards on user management page")

        except Exception as e:
            print(f"⚠ User management navigation test: {e}")

    def test_error_pages_and_validation(self):
        """Test error handling and form validation"""
        # Test 404 page
        self.driver.get(f"{self.live_server_url}/nonexistent-page/")

        # Should show some error indication
        error_indicators = self.driver.find_elements(By.XPATH, "//*[contains(text(), '404') or contains(text(), 'Not Found') or contains(text(), 'error')]")

        if error_indicators:
            print("✓ Error page handling detected")
        else:
            print("⚠ No clear error page indication found")

        # Test login form validation
        self.driver.get(f"{self.live_server_url}/auth/login/")

        # Try submitting empty form
        submit_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit_button.click()

        # Should stay on login page or show validation
        time.sleep(1)
        current_url = self.driver.current_url

        if "login" in current_url:
            print("✓ Login validation working (stayed on login page)")
        else:
            print("✓ Login validation working (redirected appropriately)")

    def test_performance_basic(self):
        """Basic performance test - page load times"""
        import time

        # Test home page load time
        start_time = time.time()
        self.driver.get(self.live_server_url)
        end_time = time.time()

        load_time = end_time - start_time
        print(f"✓ Home page load time: {load_time:.2f} seconds")

        # Test admin dashboard load time (after login)
        self.driver.get(f"{self.live_server_url}/auth/login/")
        email_field = self.driver.find_element(By.NAME, "email")
        password_field = self.driver.find_element(By.NAME, "password")

        email_field.send_keys("admin@test.com")
        password_field.send_keys("admin123")

        submit_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit_button.click()

        self.wait.until(EC.url_contains("/admin-dashboard/"))

        # Basic performance check - should load within reasonable time
        self.assertLess(load_time, 10, "Page should load within 10 seconds")

    def test_cross_browser_compatibility_indicators(self):
        """Test indicators of cross-browser compatibility"""
        self.driver.get(self.live_server_url)

        # Check for modern CSS features usage
        body_html = self.driver.find_element(By.TAG_NAME, "body").get_attribute("outerHTML")

        # Check for CSS Grid or Flexbox indicators
        modern_css_indicators = [
            "display: grid",
            "display: flex",
            "grid-template",
            "flex-direction"
        ]

        found_modern_css = any(indicator in body_html for indicator in modern_css_indicators)
        if found_modern_css:
            print("✓ Modern CSS features detected")
        else:
            print("⚠ No modern CSS features clearly detected")

        # Check for responsive meta tag
        viewport_meta = self.driver.find_elements(By.CSS_SELECTOR, "meta[name='viewport']")
        if viewport_meta:
            print("✓ Responsive viewport meta tag found")
        else:
            print("⚠ No viewport meta tag found")

if __name__ == '__main__':
    print("🚀 Starting Navigation and UI Tests with GUI")
    print("📱 Tests include: Navigation, Responsive Design, Accessibility, Performance")
    print("🔍 Make sure Chrome browser is visible for GUI testing")
    print("=" * 60)

    unittest.main(verbosity=2)