#!/usr/bin/env python
"""
Selenium tests for CrewUp Campaign Management functionality
"""
import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class CampaignManagementTester:
    def __init__(self, base_url="http://127.0.0.1:8000"):
        self.base_url = base_url
        self.driver = None

    def setup_driver(self):
        """Setup Chrome driver with options"""
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')

        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.implicitly_wait(10)

    def teardown_driver(self):
        """Close the driver"""
        if self.driver:
            self.driver.quit()

    def wait_for_element(self, by, value, timeout=10):
        """Wait for element to be present"""
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )

    def login_as_brand(self):
        """Login as a brand user for testing"""
        print("Logging in as brand user...")
        self.driver.get(f"{self.base_url}/auth/login/")

        try:
            # Wait for login form
            username_field = self.wait_for_element(By.NAME, "username")
            password_field = self.driver.find_element(By.NAME, "password")

            # Enter credentials (assuming test brand user exists)
            username_field.send_keys("test@example.com")
            password_field.send_keys("testpass123")

            # Submit form
            login_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            login_button.click()

            # Wait for redirect to dashboard
            time.sleep(2)

            # Check if login successful
            if "dashboard" in self.driver.current_url.lower() or "brand" in self.driver.current_url.lower():
                print("Successfully logged in as brand user")
                return True
            else:
                print("Login failed or not redirected to dashboard")
                return False

        except Exception as e:
            print(f"Error during login: {e}")
            return False

    def login_as_influencer(self):
        """Login as an influencer user for testing"""
        print("Logging in as influencer user...")
        self.driver.get(f"{self.base_url}/auth/login/")

        try:
            username_field = self.wait_for_element(By.NAME, "username")
            password_field = self.driver.find_element(By.NAME, "password")

            username_field.send_keys("test@example.com")
            password_field.send_keys("testpass123")

            login_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            login_button.click()

            time.sleep(2)

            if "dashboard" in self.driver.current_url.lower() or "influencer" in self.driver.current_url.lower():
                print("Successfully logged in as influencer user")
                return True
            else:
                print("Login failed or not redirected to dashboard")
                return False

        except Exception as e:
            print(f"Error during login: {e}")
            return False

    def test_create_campaign(self):
        """Test creating a new campaign"""
        print("\nTesting Campaign Creation...")

        if not self.login_as_brand():
            print("Cannot test campaign creation without brand login")
            return

        try:
            # Navigate to campaign creation page
            self.driver.get(f"{self.base_url}/campaigns/create/")

            # Wait for form to load
            title_field = self.wait_for_element(By.NAME, "title")
            print("✓ Campaign creation form loaded")

            # Fill out the form
            title_field.send_keys("Test Campaign - Selenium Automation")

            # Description
            desc_field = self.driver.find_element(By.NAME, "description")
            desc_field.send_keys("This is a test campaign created by Selenium automation testing.")

            # Budget
            budget_field = self.driver.find_element(By.NAME, "budget")
            budget_field.send_keys("1500")

            # Category
            category_select = self.driver.find_element(By.NAME, "category")
            category_select.send_keys("fashion")

            # Platform
            platform_select = self.driver.find_element(By.NAME, "platform")
            platform_select.send_keys("instagram")

            # Submit form
            submit_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            submit_button.click()

            # Wait for redirect
            time.sleep(3)

            # Check if campaign was created successfully
            if "campaign" in self.driver.current_url and "create" not in self.driver.current_url:
                print("✓ Campaign created successfully")
                # Extract campaign ID from URL for later tests
                current_url = self.driver.current_url
                if "/detail/" in current_url:
                    campaign_id = current_url.split("/detail/")[1].split("/")[0]
                    print(f"✓ Campaign ID: {campaign_id}")
                    return campaign_id
            else:
                print("✗ Campaign creation failed")
                return None

        except Exception as e:
            print(f"✗ Error creating campaign: {e}")
            return None

    def test_view_campaign_details(self, campaign_id=None):
        """Test viewing campaign details"""
        print("\nTesting Campaign Details View...")

        if campaign_id:
            campaign_url = f"{self.base_url}/campaigns/detail/{campaign_id}/"
        else:
            # Try to find a campaign from the list
            self.driver.get(f"{self.base_url}/campaigns/")
            try:
                first_campaign_link = self.wait_for_element(By.CSS_SELECTOR, "a[href*='/campaigns/detail/']")
                campaign_url = first_campaign_link.get_attribute("href")
                print(f"✓ Found campaign URL: {campaign_url}")
            except:
                print("✗ No campaigns found to view")
                return

        self.driver.get(campaign_url)

        try:
            # Check for campaign title
            campaign_title = self.wait_for_element(By.CSS_SELECTOR, "h1, .campaign-title")
            print(f"✓ Campaign title found: {campaign_title.text[:50]}...")

            # Check for campaign details
            campaign_details = self.driver.find_elements(By.CSS_SELECTOR, ".campaign-detail, .campaign-info")
            if campaign_details:
                print("✓ Campaign details displayed")
            else:
                print("? Campaign details may be missing")

            # Check for apply button (if influencer)
            apply_buttons = self.driver.find_elements(By.CSS_SELECTOR, "button, a")
            apply_found = any("apply" in btn.text.lower() or "join" in btn.text.lower()
                            for btn in apply_buttons if btn.is_displayed())
            if apply_found:
                print("✓ Apply/Join button found")
            else:
                print("✓ No apply button (expected for brand view)")

        except Exception as e:
            print(f"✗ Error viewing campaign details: {e}")

    def test_edit_campaign(self, campaign_id=None):
        """Test editing an existing campaign"""
        print("\nTesting Campaign Editing...")

        if not campaign_id:
            print("✗ No campaign ID provided for editing")
            return

        if not self.login_as_brand():
            print("✗ Cannot test campaign editing without brand login")
            return

        try:
            # Navigate to campaign edit page
            edit_url = f"{self.base_url}/campaigns/{campaign_id}/edit/"
            self.driver.get(edit_url)

            # Wait for form to load
            title_field = self.wait_for_element(By.NAME, "title")
            print("✓ Campaign edit form loaded")

            # Modify the title
            current_title = title_field.get_attribute("value")
            new_title = current_title + " - Edited"
            title_field.clear()
            title_field.send_keys(new_title)

            # Modify description
            desc_field = self.driver.find_element(By.NAME, "description")
            current_desc = desc_field.get_attribute("value")
            new_desc = current_desc + " (Edited via Selenium)"
            desc_field.clear()
            desc_field.send_keys(new_desc)

            # Submit form
            submit_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            submit_button.click()

            # Wait for redirect
            time.sleep(3)

            # Check if edit was successful
            if "campaign" in self.driver.current_url:
                print("✓ Campaign edited successfully")
            else:
                print("✗ Campaign editing failed")

        except Exception as e:
            print(f"✗ Error editing campaign: {e}")

    def test_delete_campaign(self, campaign_id=None):
        """Test deleting a campaign"""
        print("\nTesting Campaign Deletion...")

        if not campaign_id:
            print("✗ No campaign ID provided for deletion")
            return

        if not self.login_as_brand():
            print("✗ Cannot test campaign deletion without brand login")
            return

        try:
            # Navigate to campaign detail page
            detail_url = f"{self.base_url}/campaigns/detail/{campaign_id}/"
            self.driver.get(detail_url)

            # Look for delete button/link
            delete_buttons = self.driver.find_elements(By.CSS_SELECTOR,
                "button, a, input[type='submit']")

            delete_found = False
            for btn in delete_buttons:
                if "delete" in btn.text.lower() and btn.is_displayed():
                    delete_found = True
                    print("✓ Delete button found")

                    # Click delete button (this might show confirmation)
                    btn.click()
                    time.sleep(2)

                    # Look for confirmation dialog
                    confirm_buttons = self.driver.find_elements(By.CSS_SELECTOR,
                        "button, input[type='submit']")
                    confirm_found = any("confirm" in btn.text.lower() or
                                      "yes" in btn.text.lower() or
                                      "delete" in btn.text.lower()
                                      for btn in confirm_buttons if btn.is_displayed())

                    if confirm_found:
                        print("✓ Delete confirmation dialog appeared")
                        # Don't actually delete in testing
                        print("✓ Test completed - delete confirmation works")
                        return
                    else:
                        print("? No confirmation dialog found")
                        return

            if not delete_found:
                print("✗ Delete button not found")

        except Exception as e:
            print(f"✗ Error testing campaign deletion: {e}")

    def test_apply_to_campaign(self, campaign_id=None):
        """Test applying to a campaign as an influencer"""
        print("\nTesting Campaign Application...")

        if not self.login_as_influencer():
            print("✗ Cannot test campaign application without influencer login")
            return

        if campaign_id:
            campaign_url = f"{self.base_url}/campaigns/detail/{campaign_id}/"
        else:
            # Find a campaign to apply to
            self.driver.get(f"{self.base_url}/campaigns/")
            try:
                first_campaign_link = self.wait_for_element(By.CSS_SELECTOR, "a[href*='/campaigns/detail/']")
                campaign_url = first_campaign_link.get_attribute("href")
                print(f"✓ Found campaign to apply to: {campaign_url}")
            except:
                print("✗ No campaigns found to apply to")
                return

        self.driver.get(campaign_url)

        try:
            # Look for apply button
            apply_buttons = self.driver.find_elements(By.CSS_SELECTOR,
                "button, a, input[type='submit']")

            apply_found = False
            for btn in apply_buttons:
                if ("apply" in btn.text.lower() or
                    "join" in btn.text.lower()) and btn.is_displayed():
                    apply_found = True
                    print("✓ Apply button found")

                    # Click apply button
                    btn.click()
                    time.sleep(3)

                    # Check if application was successful
                    success_messages = self.driver.find_elements(By.CSS_SELECTOR,
                        ".success, .alert-success, .message")
                    success_texts = [msg.text.lower() for msg in success_messages if msg.is_displayed()]

                    if any("success" in text or "applied" in text or "submitted" in text
                          for text in success_texts):
                        print("✓ Campaign application successful")
                    elif "already applied" in self.driver.page_source.lower():
                        print("✓ Already applied to this campaign")
                    else:
                        print("? Application status unclear")
                    return

            if not apply_found:
                print("✗ Apply button not found")

        except Exception as e:
            print(f"✗ Error applying to campaign: {e}")

    def run_all_tests(self):
        """Run all campaign management tests"""
        print("Starting CrewUp Campaign Management Tests")
        print("=" * 60)

        self.setup_driver()

        try:
            # Test campaign creation
            campaign_id = self.test_create_campaign()

            # Test viewing campaign details
            self.test_view_campaign_details(campaign_id)

            # Test editing campaign
            if campaign_id:
                self.test_edit_campaign(campaign_id)

                # Test deleting campaign
                self.test_delete_campaign(campaign_id)

            # Test applying to campaign
            self.test_apply_to_campaign(campaign_id)

        finally:
            self.teardown_driver()

        print("\n" + "=" * 60)
        print("Campaign management testing completed!")

if __name__ == "__main__":
    tester = CampaignManagementTester()
    tester.run_all_tests()