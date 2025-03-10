from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time

driver = webdriver.Chrome()

# Open LinkedIn login page
driver.get("https://www.linkedin.com/login")
time.sleep(3)  # Allow time for page to load

# Get page source
html_source = driver.page_source

# Save HTML to a text file
with open("linkedin_login_page.html", "w", encoding="utf-8") as file:
    file.write(html_source)

driver.quit()

print("HTML saved successfully!")
