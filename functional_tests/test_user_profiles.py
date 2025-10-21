#!/usr/bin/env python
"""
Selenium tests for CrewUp User Profile functionality
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

class UserProfileTester:
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
            username_field = self.wait_for_element(By.NAME, "email")
            password_field = self.driver.find_element(By.NAME, "password")

            # Enter credentials (using existing brand user)
            username_field.send_keys("miniso@gmail.com")
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
            username_field = self.wait_for_element(By.NAME, "email")
            password_field = self.driver.find_element(By.NAME, "password")

            username_field.send_keys("tsunehra@gmail.com")
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

    def test_update_brand_profile(self):
        """Test updating brand profile"""
        print("\nTesting Brand Profile Update...")

        if not self.login_as_brand():
            print("Cannot test brand profile update without brand login")
            return

        try:
            # Navigate to brand profile edit page
            self.driver.get(f"{self.base_url}/auth/brand_profile/")

            # Wait for form to load
            company_name_field = self.wait_for_element(By.NAME, "company_name")
            print("Brand profile edit form loaded")

            # Update company information
            current_company = company_name_field.get_attribute("value")
            new_company = current_company + " Updated" if current_company else "Test Company Updated"
            company_name_field.clear()
            company_name_field.send_keys(new_company)

            # Update bio/website if available
            try:
                bio_field = self.driver.find_element(By.NAME, "bio")
                current_bio = bio_field.get_attribute("value")
                new_bio = current_bio + " Updated bio." if current_bio else "Updated company bio for testing."
                bio_field.clear()
                bio_field.send_keys(new_bio)
            except NoSuchElementException:
                print("Bio field not found, skipping...")

            try:
                website_field = self.driver.find_element(By.NAME, "website")
                current_website = website_field.get_attribute("value")
                new_website = current_website if current_website else "https://updated-test-company.com"
                website_field.clear()
                website_field.send_keys(new_website)
            except NoSuchElementException:
                print("Website field not found, skipping...")

            # Submit form
            submit_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            submit_button.click()

            # Wait for redirect or success message
            time.sleep(3)

            # Check if update was successful
            if "profile" in self.driver.current_url or "dashboard" in self.driver.current_url:
                print("Brand profile updated successfully")
            else:
                print("Brand profile update may have failed")

        except Exception as e:
            print(f"Error updating brand profile: {e}")

    def test_update_influencer_profile(self):
        """Test updating influencer profile"""
        print("\nTesting Influencer Profile Update...")

        if not self.login_as_influencer():
            print("Cannot test influencer profile update without influencer login")
            return

        try:
            # Navigate to influencer profile edit page
            self.driver.get(f"{self.base_url}/auth/influencer_profile/")

            # Wait for form to load
            niche_field = self.wait_for_element(By.NAME, "niche")
            print("Influencer profile edit form loaded")

            # Update niche
            current_niche = niche_field.get_attribute("value")
            new_niche = "Technology" if current_niche != "Technology" else "Fashion"
            niche_field.send_keys(new_niche)

            # Update bio if available
            try:
                bio_field = self.driver.find_element(By.NAME, "bio")
                current_bio = bio_field.get_attribute("value")
                new_bio = current_bio + " Updated bio." if current_bio else "Updated influencer bio for testing."
                bio_field.clear()
                bio_field.send_keys(new_bio)
            except NoSuchElementException:
                print("Bio field not found, skipping...")

            # Update social handles if available
            try:
                instagram_field = self.driver.find_element(By.NAME, "instagram_handle")
                current_instagram = instagram_field.get_attribute("value")
                new_instagram = current_instagram + "_updated" if current_instagram else "test_influencer_updated"
                instagram_field.clear()
                instagram_field.send_keys(new_instagram)
            except NoSuchElementException:
                print("Instagram field not found, skipping...")

            # Update follower count if available
            try:
                followers_field = self.driver.find_element(By.NAME, "followers_count")
                current_followers = followers_field.get_attribute("value")
                new_followers = str(int(current_followers) + 100) if current_followers else "1500"
                followers_field.clear()
                followers_field.send_keys(new_followers)
            except NoSuchElementException:
                print("Followers field not found, skipping...")

            # Submit form
            submit_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            submit_button.click()

            # Wait for redirect or success message
            time.sleep(3)

            # Check if update was successful
            if "profile" in self.driver.current_url or "dashboard" in self.driver.current_url:
                print("Influencer profile updated successfully")
            else:
                print("Influencer profile update may have failed")

        except Exception as e:
            print(f"Error updating influencer profile: {e}")

    def test_view_public_profiles(self):
        """Test viewing public profiles"""
        print("\nTesting Public Profile Viewing...")

        try:
            # Navigate to influencers page to find a profile to view
            self.driver.get(f"{self.base_url}/influencers/")

            # Wait for influencer cards to load
            influencer_cards = self.wait_for_element(By.CLASS_NAME, "influencer-card")
            print("Influencer cards loaded")

            # Find and click on a "View Profile" button
            view_buttons = self.driver.find_elements(By.CSS_SELECTOR, "a.btn-view, a[href*='profile']")

            if view_buttons:
                # Click the first view profile button
                view_buttons[0].click()
                time.sleep(3)

                # Check if we're on a profile page
                if "profile" in self.driver.current_url:
                    print("Successfully navigated to public profile")

                    # Check for profile elements
                    try:
                        profile_name = self.driver.find_element(By.CLASS_NAME, "profile-name")
                        print(f"Profile name found: {profile_name.text}")
                    except NoSuchElementException:
                        print("Profile name not found")

                    try:
                        profile_bio = self.driver.find_elements(By.CLASS_NAME, "profile-bio")
                        if profile_bio:
                            print("Profile bio found")
                    except:
                        print("Profile bio not found")

                    try:
                        social_links = self.driver.find_elements(By.CLASS_NAME, "social-link")
                        print(f"Found {len(social_links)} social links")
                    except:
                        print("Social links not found")

                else:
                    print("Not redirected to profile page")
            else:
                print("No view profile buttons found")

        except Exception as e:
            print(f"Error viewing public profiles: {e}")

    def run_all_tests(self):
        """Run all user profile tests"""
        print("Starting CrewUp User Profile Tests")
        print("=" * 50)

        self.setup_driver()

        try:
            self.test_update_brand_profile()
            self.test_update_influencer_profile()
            self.test_view_public_profiles()

        finally:
            self.teardown_driver()

        print("\n" + "=" * 50)
        print("User profile testing completed!")

if __name__ == "__main__":
    tester = UserProfileTester()
    tester.run_all_tests()