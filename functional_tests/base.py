# tests/functional/base.py
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.urls import reverse, NoReverseMatch
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import os, time

class FunctionalTest(StaticLiveServerTestCase):
    """Base test class for Selenium functional tests."""

    # ---------- CONFIG YOU CAN OVERRIDE PER PROJECT ----------
    LOGIN_URL_NAMES = ("authentication:login", "login", "account_login", "auth_login")
    LOGIN_PATH_FALLBACKS = ("/auth/login/", "/accounts/login/", "/users/login/", "/login/")
    DASHBOARD_URL_NAMES = ("dashboard", "brand_dashboard", "influencer_dashboard", "admin_dashboard")
    DASHBOARD_PATH_FALLBACKS = ("/dashboard/", "/brand-dashboard/", "/influencer-dashboard/", "/admin-dashboard/", "/")
    LOGOUT_URL_NAMES = ("authentication:logout", "logout", "account_logout", "auth_logout")
    LOGOUT_PATH_FALLBACKS = ("/auth/logout/", "/accounts/logout/", "/logout/")
    CONTACT_URL_NAMES = ("contact", "contact_us")
    CONTACT_PATH_FALLBACKS = ("/contact/", "/support/contact/")
    # ---------------------------------------------------------

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        chrome_options = Options()
        # Headless / GPU behavior configurable via environment
        # E2E_HEADLESS=0 to show Chrome UI; E2E_USE_GPU=1 to allow GPU; E2E_SHOW_GPU_PAGE=1 to open chrome://gpu
        HEADLESS = os.getenv("E2E_HEADLESS", "1") != "0"
        if HEADLESS:
            chrome_options.add_argument("--headless=new")
        else:
            # Helpful when you want to inspect tabs while tests run
            chrome_options.add_argument("--remote-debugging-port=9222")
            chrome_options.add_argument("--auto-open-devtools-for-tabs")
        
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")

        USE_GPU = os.getenv("E2E_USE_GPU", "1") == "1"
        if not USE_GPU:
            # Keep disabled on CI by default
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--disable-software-rasterizer")

        # Try Selenium Manager first (included in Selenium 4.6+)
        # This will automatically find a compatible ChromeDriver
        try:
            cls.driver = webdriver.Chrome(options=chrome_options)
        except Exception as e:
            print(f"Selenium Manager failed with: {e}")
            # If Selenium Manager fails, try with the downloaded ChromeDriver
            try:
                service = Service(executable_path=r"D:\CrewUp Project\chromedriver-win64\chromedriver.exe")
                cls.driver = webdriver.Chrome(service=service, options=chrome_options)
            except Exception as e2:
                print(f"Downloaded ChromeDriver failed with: {e2}")
                # Final fallback: try with a specific ChromeDriver version via manager
                try:
                    service = Service(ChromeDriverManager(version="141.0.7390.86").install())
                    cls.driver = webdriver.Chrome(service=service, options=chrome_options)
                except Exception as e3:
                    print(f"ChromeDriver 141.0.7390.86 failed with: {e3}")
                    # Last resort: latest via manager
                    try:
                        service = Service(ChromeDriverManager().install())
                        cls.driver = webdriver.Chrome(service=service, options=chrome_options)
                    except Exception as e4:
                        raise RuntimeError(
                            "Failed to initialize Chrome WebDriver. "
                            f"Selenium Manager error: {e}\n"
                            f"Downloaded ChromeDriver error: {e2}\n"
                            f"ChromeDriver 141 error: {e3}\n"
                            f"Latest ChromeDriver error: {e4}"
                        ) from e4

        cls.driver.implicitly_wait(10)

        # Optionally open chrome://gpu in a separate tab so you can see GPU/virtualization state
        if os.getenv("E2E_SHOW_GPU_PAGE", "0") == "1":
            try:
                default_handle = cls.driver.current_window_handle
                cls.driver.switch_to.new_window('tab')
                cls.driver.get("chrome://gpu")
                # Switch back to the default tab for tests
                cls.driver.switch_to.window(default_handle)
            except Exception as e:
                print(f"Unable to open chrome://gpu: {e}")

        cls.screenshots_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "screenshots"
        )
        os.makedirs(cls.screenshots_dir, exist_ok=True)

        cls.pages_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "pages"
        )
        os.makedirs(cls.pages_dir, exist_ok=True)

    @classmethod
    def tearDownClass(cls):
        try:
            cls.driver.quit()
        finally:
            super().tearDownClass()

    def _pytest_failed(self) -> bool:
        """
        Best-effort detection of failure under both unittest and pytest.
        Never raise here.
        """
        try:
            outcome = getattr(self, "_outcome", None)
            if not outcome:
                return False

            # Python 3.11+ often has .result with .failures/.errors
            result = getattr(outcome, "result", None)
            if result:
                fails = getattr(result, "failures", []) or []
                errs = getattr(result, "errors", []) or []
                return any(test is self for test, _ in fails + errs)

            # Older style: .errors present on outcome
            errors = getattr(outcome, "errors", None)
            if errors:
                return any(exc for _, exc in errors)

        except Exception:
            # Never break teardown
            return False
        return False

    def tearDown(self):
        try:
            if self._pytest_failed():
                self.take_screenshot(self.id().split(".")[-1])
                self.dump_page(self.id().split(".")[-1])  # also dump HTML for debugging
        finally:
            super().tearDown()

    def take_screenshot(self, name: str) -> str:
        ts = time.strftime("%Y%m%d-%H%M%S")
        path = os.path.join(self.screenshots_dir, f"{name}_{ts}.png")
        self.driver.save_screenshot(path)
        return path

    def dump_page(self, name: str) -> str:
        """Save current page HTML to help debug selector/URL issues."""
        ts = time.strftime("%Y%m%d-%H%M%S")
        path = os.path.join(self.pages_dir, f"{name}_{ts}.html")
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.driver.page_source)
        return path

    # --------- Wait helpers ---------
    def wait_for_element(self, by: By, value: str, timeout: int = 10):
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )

    def wait_for_clickable(self, by: By, value: str, timeout: int = 10):
        return WebDriverWait(self.driver, timeout).until(
            EC.element_to_be_clickable((by, value))
        )

    def wait_for_url_contains(self, text: str, timeout: int = 10):
        return WebDriverWait(self.driver, timeout).until(lambda d: text in d.current_url)

    # --------- URL resolvers ---------
    def _resolve_url_by_names(self, names):
        from django.urls import reverse
        for name in names:
            try:
                return self.live_server_url + reverse(name)
            except NoReverseMatch:
                continue
        return None

    def resolve_login_url(self) -> str:
        url = self._resolve_url_by_names(self.LOGIN_URL_NAMES)
        if url:
            return url
        # fallback by paths (first that exists)
        return self.live_server_url + self.LOGIN_PATH_FALLBACKS[0]

    def resolve_dashboard_url(self) -> str:
        url = self._resolve_url_by_names(self.DASHBOARD_URL_NAMES)
        if url:
            return url
        return self.live_server_url + self.DASHBOARD_PATH_FALLBACKS[0]

    def resolve_contact_url(self) -> str:
        url = self._resolve_url_by_names(self.CONTACT_URL_NAMES)
        if url:
            return url
        return self.live_server_url + self.CONTACT_PATH_FALLBACKS[0]

    def resolve_logout_url(self) -> str:
        url = self._resolve_url_by_names(self.LOGOUT_URL_NAMES)
        if url:
            return url
        return self.live_server_url + self.LOGOUT_PATH_FALLBACKS[0]

    # --------- Element helpers ---------
    def _find_first(self, selectors):
        """
        Try a list of CSS selectors; return element or raise NoSuchElementException.
        """
        last_exc = None
        for sel in selectors:
            try:
                return self.driver.find_element(By.CSS_SELECTOR, sel)
            except NoSuchElementException as e:
                last_exc = e
        raise last_exc

    def _error_text_guess(self) -> str:
        """
        Try common error containers and return first non-empty text (lowercased).
        """
        candidates = [
            ".error-message", ".alert", ".alert-danger", ".invalid-feedback",
            ".help-block", ".nonfield", ".errorlist li", ".text-danger", ".bg-red-50"
        ]
        for sel in candidates:
            try:
                el = WebDriverWait(self.driver, 3).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, sel))
                )
                txt = (el.text or "").strip()
                if txt:
                    return txt
            except Exception:
                pass
        return ""

    # --------- Auth flow ---------
    def login(self, username: str, password: str, redirect_contains: str = "dashboard"):
        url = self.resolve_login_url()
        self.driver.get(url)

        try:
            self.wait_for_element(By.CSS_SELECTOR, "form")
        except TimeoutException:
            self.dump_page("login_no_form")
            raise AssertionError(f"Login form not found at {url}")

        # Accept either email or username field (prefer email)
        user_field = None
        for sel in ['input[name="email"]', '#email', 'input[type="email"]', 'input[name="username"]']:
            try:
                user_field = self.driver.find_element(By.CSS_SELECTOR, sel)
                break
            except NoSuchElementException:
                continue
        if not user_field:
            self.dump_page("login_no_user_field")
            raise AssertionError("No username/email input found on login page")

        user_field.clear()
        user_field.send_keys(username)

        # Try multiple selectors for password to be robust
        pwd = None
        for sel in ['input[name="password"]', '#password', 'input[type="password"]']:
            try:
                pwd = self.driver.find_element(By.CSS_SELECTOR, sel)
                break
            except NoSuchElementException:
                continue
        if not pwd:
            self.dump_page("login_no_password")
            raise AssertionError("No password input found on login page")

        pwd.clear()
        pwd.send_keys(password)

        # Submit
        try:
            self.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
        except NoSuchElementException:
            self._find_first(["form button", "button.submit", "input[type='submit']"]).click()

        # Wait for redirect
        self.wait_for_url_contains(redirect_contains)
