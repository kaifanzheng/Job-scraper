import time
import json
import random
import pytesseract
import pyautogui
import cv2
import numpy as np
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

                # Scroll & Capture Full Job Details using Mouse Scroll
                job_text = self.extract_full_job_details(index)

                print(f"\n📌 Job {index + 1} Details:\n{job_text}\n")

                self.jobs_data.append({
                    "job_details": job_text
                })

            except Exception as e:
                print(f"⚠️ Error interacting with job: {e}")

    def click_show_more(self, screenshot_path):
        """Detect and click 'Show More' button using OCR and PyAutoGUI."""
        try:
            # Load the image
            image = cv2.imread(screenshot_path)

            if image is None:
                print("⚠️ Error: Unable to load the screenshot.")
                return

            # Get image dimensions
            height, width, _ = image.shape

            # Focus only on the **bottom half** where the "Show More" button is likely located
            bottom_half = image[height // 2 :, :]

            # Convert to grayscale
            gray = cv2.cvtColor(bottom_half, cv2.COLOR_BGR2GRAY)

            # Apply OCR to detect text
            extracted_text = pytesseract.image_to_data(gray, output_type=pytesseract.Output.DICT)

            # Find occurrences of "Show More"
            for i, text in enumerate(extracted_text["text"]):
                if "Show" in text or "More" in text:  # Allow slight OCR tolerance
                    x, y, w, h = (
                        extracted_text["left"][i],
                        extracted_text["top"][i] + height // 2,  # Adjust Y coordinate to full image
                        extracted_text["width"][i],
                        extracted_text["height"][i],
                    )

                    # Convert image coordinates to screen coordinates
                    screen_width, screen_height = pyautogui.size()
                    screen_x = int(x * (screen_width / width))+30
                    screen_y = int(y * (screen_height / height)) + 50  # Move cursor **10 pixels down**

                    print(f"✅ 'Show More' button detected at ({screen_x}, {screen_y}). Clicking...")

                    # Move the mouse and click
                    pyautogui.moveTo(screen_x, screen_y, duration=random.uniform(0.5, 1.5))
                    pyautogui.click()

                    time.sleep(random.uniform(2, 4))

                    return  # Exit after first detection

            print("⚠️ 'Show More' button not detected.")

        except Exception as e:
            print(f"⚠️ Error detecting 'Show More' button: {e}")

    def close_popup(self):
        """Close the 'Never Miss an Opportunity' pop-up if detected."""
        print("🔍 Closing pop-up...")
        pyautogui.moveTo(900, 280, duration=random.uniform(0.5, 1.5))
        pyautogui.click()
        time.sleep(random.uniform(2, 4))
        print("✅ Pop-up closed.")

    def extract_full_job_details(self, job_index):
        """Scroll down inside the job details tab using mouse wheel and capture text until 'Show Less' is detected."""
        full_text = []
        screenshot_counter = 1
        showmore_button_counter = 0
        while True:
            # Capture the current job panel
            screenshot_path = f"screen_shot/job_details_{job_index}_{screenshot_counter}.png"
            self.driver.save_screenshot(screenshot_path)
            time.sleep(2)

            # Extract text from screenshot
            image = Image.open(screenshot_path)
            extracted_text = pytesseract.image_to_string(image).strip()

            if extracted_text:
                full_text.append(extracted_text)

            print(f"📸 Captured and processed screenshot {screenshot_counter} for job {job_index + 1}")
            print(f"🔍 Extracted Text: {extracted_text}")

            # Check if "Show Less" button is visible (stop scrolling)
            if "Showless" in extracted_text:
                print("✅ 'Showless' detected, all job details captured.")
                break
            if screenshot_counter >= 5:
                print("🛑 Maximum screenshots reached. Stopping extraction.")
                break
            if showmore_button_counter >= 2:
                print("🛑 repeatly detecting Showmore button")
                break
            if "Showmore" in extracted_text:
                print("✅ 'Showmore' detected in the screen shot.it detected: ",showmore_button_counter)
                self.click_show_more(screenshot_path=screenshot_path)
                showmore_button_counter = showmore_button_counter + 1
                continue
            if "Never Miss an Opportunity" in extracted_text:
                print("🛑 pop up window showed up.")
                self.close_popup()
                continue

            # **Use mouse scroll wheel to scroll down inside job details tab**
            pyautogui.scroll(-7)  # Scroll down (negative value)
            time.sleep(random.uniform(2, 4))

            screenshot_counter += 1

        return "\n".join(full_text)

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