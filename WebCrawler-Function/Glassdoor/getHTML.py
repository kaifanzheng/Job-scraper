import undetected_chromedriver as uc
import time
import random

# Set up undetected Chrome Driver with human-like options
options = uc.ChromeOptions()
options.add_argument("--disable-blink-features=AutomationControlled")  # Prevent detection
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
options.add_argument("--disable-gpu")  # Useful for headless mode
options.add_argument("--start-maximized")  # Maximize window
options.add_argument("--incognito")  # Use Incognito Mode to avoid tracking

# Start undetected Chrome
driver = uc.Chrome(options=options)

# Target URL
url = "https://www.glassdoor.com/Job/jobs.htm?sc.keyword=Software%20Engineer"

# Visit the page
driver.get(url)

# Random delay to avoid detection
time.sleep(random.uniform(5, 10))

# Get page source (HTML)
html_source = driver.page_source

# Save HTML to a text file
with open("glassdoor_jobs.html", "w", encoding="utf-8") as file:
    file.write(html_source)

print("HTML saved successfully as 'glassdoor_jobs.html'")

# Close browser
driver.quit()
