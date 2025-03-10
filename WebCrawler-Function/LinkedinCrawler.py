from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time

# Set up Chrome WebDriver
def setup_driver():
    driver = webdriver.Chrome()
    return driver

def login_to_linkedin(driver, username, password):
    # Open LinkedIn Login Page
    driver.get("https://www.linkedin.com/login")
    
    try:
        # Wait for the login form to load
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "username")))
        
        # Enter username and password
        driver.find_element(By.ID, "username").send_keys(username)
        driver.find_element(By.ID, "password").send_keys(password)
        
        # Click the Sign in button (ensure the selector matches latest LinkedIn structure)
        sign_in_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//button[contains(@class, "btn__primary--large")]'))
        )
        sign_in_button.click()

        # Wait to confirm login success by checking for a post-login element (e.g., the feed search bar)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "global-nav-typeahead")))
        print("Login successful!")
        return True

    except TimeoutException:
        # If login fails, check for an error message on the login page
        try:
            error_msg = driver.find_element(By.ID, "error-for-password")
            if error_msg.is_displayed():
                print(f"Login failed: {error_msg.text}")
        except NoSuchElementException:
            print("Login failed: No post-login element detected and no error message found.")
        return False

if __name__ == "__main__":
    # Set up the driver
    driver = setup_driver()

    # Replace with your LinkedIn credentials
    username = "zhengkaifan73@gmail.com"
    password = "zkf20001212"

    # Run the login function
    login_success = login_to_linkedin(driver, username, password)

    # Close the browser
    driver.quit()
