from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time, random


def login_to_linkedin(username: str, password: str, proxy: str = None):
    """
    Logs into LinkedIn with the given username and password, using human-like interactions.
    Features:
      - Randomized typing speed for entering credentials.
      - Mouse movement to hover over elements before clicking.
      - Optional proxy support for rotating IP addresses.
    Ensures stability with proper waits and exception handling.
    """
    driver = None
    try:
        # Setup Chrome options (e.g., for proxy)
        chrome_options = webdriver.ChromeOptions()
        if proxy:
            chrome_options.add_argument(f'--proxy-server={proxy}')
        # Initialize WebDriver (Chrome in this example) with options
        driver = webdriver.Chrome(options=chrome_options)
        driver.get("https://www.linkedin.com/login")
        
        # Wait for the login form elements to load
        wait = WebDriverWait(driver, 10)
        username_field = wait.until(EC.element_to_be_clickable((By.ID, "username")))
        password_field = wait.until(EC.element_to_be_clickable((By.ID, "password")))
        
        # Type the username with human-like random delays
        for char in username:
            username_field.send_keys(char)
            time.sleep(random.uniform(0.1, 0.3))  # random delay between keystrokes
        
        # Type the password with human-like random delays
        for char in password:
            password_field.send_keys(char)
            time.sleep(random.uniform(0.1, 0.3))
        
        # Locate the Sign In button (using its type or text)
        sign_in_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']")))
        
        # Move mouse to the Sign In button before clicking (to simulate hover)
        actions = ActionChains(driver)
        actions.move_to_element(sign_in_btn).pause(random.uniform(0.2, 0.5)).click(sign_in_btn).perform()
        
        # Optionally, wait a moment for post-login page to load (or verify successful login)
        WebDriverWait(driver, 10).until(EC.url_contains("/feed"))  # waits until redirected to feed/home
    except Exception as e:
        # Handle any errors during login
        print(f"[ERROR] LinkedIn login failed: {e}")
        if driver:
            driver.quit()  # close the browser if it was opened
        raise  # re-raise the exception after cleanup, or return False as needed
    return driver  # return the logged-in WebDriver instance for further use

def scrape_jobs_page(driver):
    """
    Navigates to LinkedIn's recommended jobs page, extracts its HTML, and saves it to a file.
    
    Args:
        driver: The logged-in Selenium WebDriver instance.
    
    Returns:
        bool: True if successful, False if an error occurs.
    """
    try:
        # Navigate to LinkedIn Recommended Jobs page
        print("🔄 Navigating to LinkedIn Recommended Jobs page...")
        driver.get("https://www.linkedin.com/jobs/collections/recommended")
        
        # Wait to allow full page load
        time.sleep(5)  # Give extra time for LinkedIn to load content
        
        # Debugging: Check if page is loaded
        print("Current URL:", driver.current_url)  # Check if redirected
        driver.save_screenshot("jobs_page.png")  # Save screenshot for debugging
        
        # Check if the user is redirected (LinkedIn bot detection)
        if "checkpoint/challenge" in driver.current_url:
            print("⚠️ LinkedIn has detected a bot! You might need to solve a CAPTCHA.")
            return False

        # Wait until job listings load (try multiple strategies)
        try:
            job_section = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CLASS_NAME, "jobs-search-results"))
            )
        except:
            print("⚠️ Jobs container not found, trying alternate method...")
            job_section = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH, "//main"))
            )
        
        # Extract full page HTML
        html_source = driver.page_source

        # Save HTML content to a text file
        with open("linkedin_jobs_page.txt", "w", encoding="utf-8") as file:
            file.write(html_source)

        print("✅ Successfully scraped LinkedIn jobs page and saved to linkedin_jobs_page.txt")
        return True

    except Exception as e:
        print(f"❌ Error scraping jobs page: {e}")
        return False

        
if __name__ == "__main__":
    # Replace with your LinkedIn credentials
    USERNAME = "zhengkaifan73@gmail.com"
    PASSWORD = "zkf20001212"

    # Optional: Use a proxy (set to None to disable)
    PROXY = None  # Example: "123.45.67.89:8080"

    # Login and get the driver instance
    driver = login_to_linkedin(USERNAME, PASSWORD, PROXY)

    # If login is successful, scrape the jobs page
    if driver:
        scrape_jobs_page(driver)

        # Close the browser
        driver.quit()