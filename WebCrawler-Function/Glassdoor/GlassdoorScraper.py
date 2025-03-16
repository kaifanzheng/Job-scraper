import time
import json
import random
import pytesseract
from PIL import Image
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Set the Tesseract-OCR path (Update this path based on your OS)
pytesseract.pytesseract.tesseract_cmd = "tesseract"

class GlassdoorScraper:
    def __init__(self, url):
        self.url = url
        self.driver = self.init_driver()
        self.jobs_data = []

    def init_driver(self):
        """Initialize WebDriver with human-like settings."""
        options = Options()
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--start-maximized")
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        return driver

    def open_glassdoor(self):
        """Open Glassdoor job page."""
        self.driver.get(self.url)
        time.sleep(random.uniform(3, 5))

    def scroll_slowly(self):
        """Scroll down the page dynamically to load more jobs."""
        last_height = self.driver.execute_script("return document.body.scrollHeight")

        while True:
            self.driver.execute_script("window.scrollBy(0, 500);")
            time.sleep(random.uniform(2, 4))

            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break  # Stop scrolling if no new content is loaded
            last_height = new_height

    def find_and_click_jobs(self):
        """Visually identify and click each job listing like a human."""
        print("🔍 Scanning job listings...")

        job_list = self.driver.find_elements(By.CSS_SELECTOR, "li[data-test='jobListing']")
        print(f"✅ Found {len(job_list)} jobs.")

        for index, job in enumerate(job_list):
            try:
                self.scroll_into_view(job)
                time.sleep(random.uniform(2, 4))  # Mimic human delay
                
                # Click job listing to open details
                job.click()
                time.sleep(random.uniform(3, 6))  # Allow details to load

                # Ensure "Show More" is clicked inside job details
                self.click_show_more()

                # Extract job details visually via OCR from the full page screenshot
                job_text = self.extract_text_from_screenshot()
                
                print(f"\n📌 Job {index + 1} Details:\n{job_text}\n")

                self.jobs_data.append({
                    "job_details": job_text
                })

            except Exception as e:
                print(f"⚠️ Error interacting with job: {e}")

    def click_show_more(self):
        """Click the 'Show More' button if present to load full job description."""
        try:
            show_more_button = WebDriverWait(self.driver, 3).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Show more')]"))
            )
            self.scroll_into_view(show_more_button)
            time.sleep(random.uniform(1, 2))
            show_more_button.click()
            print("✅ Clicked 'Show More' in job description.")
            time.sleep(random.uniform(2, 4))
        except:
            pass  # No "Show More" button found

    def extract_text_from_screenshot(self):
        """Capture a screenshot of the full page and extract text using OCR."""
        try:
            screenshot_path = "full_page_screenshot.png"
            self.driver.save_screenshot(screenshot_path)
            time.sleep(2)

            # Use OCR to extract text from the image
            image = Image.open(screenshot_path)
            extracted_text = pytesseract.image_to_string(image)

            return extracted_text.strip()

        except Exception as e:
            print(f"⚠️ Error extracting job details via OCR: {e}")
            return "Error extracting job details"

    def scroll_into_view(self, element):
        """Scroll to an element smoothly."""
        self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
        time.sleep(random.uniform(1, 2))

    def save_to_json(self):
        """Save job data to a JSON file."""
        with open("glassdoor_jobs.json", "w", encoding="utf-8") as f:
            json.dump(self.jobs_data, f, indent=4, ensure_ascii=False)
        print(f"✅ Scraped {len(self.jobs_data)} jobs and saved to 'glassdoor_jobs.json'.")

    def run(self):
        """Run the full scraping process."""
        self.open_glassdoor()
        self.scroll_slowly()  # Scroll through job listings dynamically
        self.find_and_click_jobs()  # Click each job visually
        self.save_to_json()
        self.driver.quit()

# ✅ Run the scraper
if __name__ == "__main__":
    scraper = GlassdoorScraper("https://www.glassdoor.com/Job/jobs.htm?sc.keyword=Software%20Engineer")
    scraper.run()
