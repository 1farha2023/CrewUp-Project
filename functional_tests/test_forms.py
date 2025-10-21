from .base import FunctionalTest
from django.contrib.auth import get_user_model
from selenium.webdriver.common.by import By

class FormSubmissionTest(FunctionalTest):
    def setUp(self):
        super().setUp()
        User = get_user_model()
        self.username = "testuser"
        self.email = "test@example.com"
        self.password = "testpass123"
        User.objects.create_user(
            username=self.username, email=self.email, password=self.password
        )
        self.login(self.email, self.password)

    def test_contact_form_submission(self):
        self.driver.get(self.resolve_contact_url())
        data = {
            "name": "Test User",
            "email": "test@example.com",
            "subject": "Test Subject",
            "message": "This is a test message.",
        }
        for field, val in data.items():
            el = self._find_first([f'input[name="{field}"]', f'textarea[name="{field}"]'])
            el.clear()
            el.send_keys(val)

        self._find_first(['button[type="submit"]','form button','input[type="submit"]']).click()

        msg = self._error_text_guess()
        # Prefer success banners; fallback to generic “thank you”
        body_text = self.driver.find_element(By.TAG_NAME, "body").text.lower()
        assert "thank you" in (msg.lower() + " " + body_text)

    def test_form_validation(self):
        self.driver.get(self.resolve_contact_url())
        self._find_first(['button[type="submit"]','form button','input[type="submit"]']).click()

        # Any standard validation error container
        errors = self.driver.find_elements(By.CSS_SELECTOR,
            ".error-message, .errorlist li, .invalid-feedback, .help-block, .text-danger"
        )
        assert len(errors) > 0, "Expected validation errors but none found"
