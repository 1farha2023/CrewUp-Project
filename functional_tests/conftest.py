"""
Pytest configuration for functional tests.
"""
import os
import pytest
from django.conf import settings
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# Set the DJANGO_SETTINGS_MODULE if it's not set
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crewup.settings')

@pytest.fixture(scope='session')
def chrome_driver():
    """Create a Chrome WebDriver instance."""
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.implicitly_wait(10)
    driver.set_window_size(1920, 1080)
    
    yield driver
    driver.quit()

@pytest.fixture
def live_server_url(live_server):
    """
    Return the URL of the live server.
    Override to use the correct host and port.
    """
    return live_server.url
