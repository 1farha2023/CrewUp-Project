#!/usr/bin/env python
"""
Manual Selenium test script for CrewUp search functionality
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

class SearchTester:
    def __init__(self, base_url="http://127.0.0.1:8000"):
        self.base_url = base_url
        self.driver = None

    def setup_driver(self):
        """Setup Chrome driver with options"""
        chrome_options = Options()
        # chrome_options.add_argument('--headless')  # Remove headless for GUI testing
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--start-maximized')

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

    def test_influencers_search(self):
        """Test search functionality on influencers page"""
        print("Testing Influencers Search...")
        self.driver.get(f"{self.base_url}/influencers/")

        try:
            # Check if search field exists
            search_field = self.wait_for_element(By.CSS_SELECTOR, "input[name='search']")
            print("Search field found on influencers page")
            print(f"  Page title: {self.driver.title}")
            print(f"  Current URL: {self.driver.current_url}")
            print("  Testing search functionality...")

            # Test search with a term
            search_field.clear()
            search_field.send_keys("fashion")
            search_field.send_keys(Keys.RETURN)

            # Wait for results
            time.sleep(2)

            # Check if URL updated with search parameter
            current_url = self.driver.current_url
            if "search=fashion" in current_url:
                print("✓ URL updated with search parameter")
            else:
                print("URL not updated with search parameter")

            # Check for results or no results message
            try:
                results = self.driver.find_elements(By.CLASS_NAME, "influencer-card")
                print(f"Found {len(results)} influencer results")
            except:
                try:
                    no_results = self.driver.find_element(By.CLASS_NAME, "no-influencers")
                    print("✓ No results message displayed")
                except:
                    print("? No results found and no 'no results' message")

        except TimeoutException:
            print("Search field not found on influencers page")
        except Exception as e:
            print(f"Error testing influencers search: {e}")

    def test_brands_search(self):
        """Test search functionality on brands page"""
        print("\nTesting Brands Search...")
        self.driver.get(f"{self.base_url}/brands/")

        try:
            # Check if search field exists
            search_field = self.wait_for_element(By.CSS_SELECTOR, "input.search-box")
            print("Search field found on brands page")

            # Test search with a term
            search_field.clear()
            search_field.send_keys("tech")
            search_field.send_keys(Keys.RETURN)

            # Wait for results
            time.sleep(2)

            # Check if URL updated with search parameter
            current_url = self.driver.current_url
            if "search=tech" in current_url:
                print("URL updated with search parameter")
            else:
                print("X URL not updated with search parameter")

            # Check for results or no results message
            try:
                results = self.driver.find_elements(By.CLASS_NAME, "brand-card")
                print(f"✓ Found {len(results)} brand results")
            except:
                try:
                    no_results = self.driver.find_element(By.CLASS_NAME, "no-brands")
                    print("No results message displayed")
                except:
                    print("? No results found and no 'no results' message")

        except TimeoutException:
            print("X Search field not found on brands page")
        except Exception as e:
            print(f"X Error testing brands search: {e}")

    def test_campaigns_search(self):
        """Test search functionality on campaigns page"""
        print("\nTesting Campaigns Search...")
        self.driver.get(f"{self.base_url}/campaigns/")

        try:
            # Check if search field exists
            search_field = self.wait_for_element(By.ID, "search")
            print("✓ Search field found on campaigns page")

            # Test search with a term
            search_field.clear()
            search_field.send_keys("marketing")
            # Wait for debounced search (500ms)
            time.sleep(1)

            # Check if URL updated with search parameter
            current_url = self.driver.current_url
            if "search=marketing" in current_url:
                print("✓ URL updated with search parameter")
            else:
                print("✗ URL not updated with search parameter")

            # Check for results
            try:
                results = self.driver.find_elements(By.CLASS_NAME, "bg-white")
                campaigns = [r for r in results if "campaign" in r.get_attribute("class") or "rounded-lg" in r.get_attribute("class")]
                print(f"✓ Found {len(campaigns)} campaign results")
            except:
                try:
                    no_results = self.driver.find_element(By.XPATH, "//*[contains(text(), 'No campaigns found')]")
                    print("✓ No results message displayed")
                except:
                    print("? No results found and no 'no results' message")

        except TimeoutException:
            print("X Search field not found on campaigns page")
        except Exception as e:
            print(f"X Error testing campaigns search: {e}")

    def test_special_characters(self):
        """Test search with special characters"""
        print("\nTesting Special Characters Search...")
        self.driver.get(f"{self.base_url}/influencers/")

        try:
            search_field = self.wait_for_element(By.CSS_SELECTOR, "input[name='search']")
            search_field.clear()
            search_field.send_keys("!@#$%^&*()")
            search_field.send_keys(Keys.RETURN)

            time.sleep(2)

            # Check for errors
            page_source = self.driver.page_source.lower()
            if "error" in page_source or "exception" in page_source:
                print("X Error found in page after special character search")
            else:
                print("✓ No errors with special character search")

        except Exception as e:
            print(f"X Error testing special characters: {e}")

    def run_all_tests(self):
        """Run all search tests"""
        print("Starting CrewUp Search Functionality Tests")
        print("=" * 50)

        self.setup_driver()

        try:
            self.test_influencers_search()
            self.test_brands_search()
            self.test_campaigns_search()
            self.test_special_characters()

        finally:
            self.teardown_driver()

        print("\n" + "=" * 50)
        print("Search testing completed!")

if __name__ == "__main__":
    tester = SearchTester()
    tester.run_all_tests()