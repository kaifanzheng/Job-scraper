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
from webdriver_manager.chrome import ChromeDriverManager

pytesseract.pytesseract.tesseract_cmd = "tesseract"

class GlassdoorScraper:
    def __init__(self, url):
        self.url = url
        self.driver = self.init_driver()
        self.jobs_data = []

    def init_driver(self):
        options = Options()
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--start-maximized")
        return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    def open_glassdoor(self):
        self.driver.get(self.url)
        time.sleep(random.uniform(1.5, 2.5))

    def scroll_slowly(self):
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        while True:
            self.driver.execute_script("window.scrollBy(0, 500);")
            time.sleep(random.uniform(1, 1.8))
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

    def find_and_click_jobs(self):
        scraper_counter = 0
        while True:
            print("🔍 Scanning job listings...")
            job_list = self.driver.find_elements(By.CSS_SELECTOR, "li[data-test='jobListing']")
            if len(job_list) >= 150:
                print("✅ Reached Max job limit, quitting...")
                break

            print(f"✅ Found {len(job_list)} jobs.")
            job_list = job_list[scraper_counter * 30:]
            for index, job in enumerate(job_list):
                try:
                    self.scroll_into_view(job)
                    time.sleep(random.uniform(0.5, 1.2))
                    job.click()
                    time.sleep(random.uniform(1.2, 2))
                    job_text = self.extract_full_job_details(index)
                    print(f"\n📌 Job {index + 1} Details:\n{job_text[:150]}...\n")
                    self.jobs_data.append({"job_details": job_text})
                except Exception as e:
                    print(f"⚠️ Error interacting with job: {e}")

    def extract_full_job_details(self, job_index):
        full_text = []
        screenshot_counter = 1
        showmore_button_counter = 0

        while True:
            screenshot_path = f"screen_shot/job_details_{job_index}_{screenshot_counter}.png"
            self.driver.save_screenshot(screenshot_path)
            time.sleep(1.2)
            image = Image.open(screenshot_path)
            extracted_text = pytesseract.image_to_string(image).strip()

            if extracted_text:
                full_text.append(extracted_text)

            print(f"📸 Screenshot {screenshot_counter} - Extracted: {extracted_text[:60]}")

            if "Showless" in extracted_text:
                break
            if screenshot_counter >= 5:
                break
            if showmore_button_counter >= 2:
                break
            if ("Showmore" in extracted_text) or ("Show" in extracted_text) or ("More" in extracted_text):
                self.click_show_more(screenshot_path)
                showmore_button_counter += 1
                continue
            if "Never Miss an Opportunity" in extracted_text:
                self.close_popup()
                continue

            pyautogui.scroll(-7)
            time.sleep(random.uniform(1.2, 2))
            screenshot_counter += 1

        return "\n".join(full_text)

    def click_show_more(self, screenshot_path):
        try:
            image = cv2.imread(screenshot_path)
            if image is None:
                print("⚠️ Error: Unable to load the screenshot.")
                return

            height, width, _ = image.shape
            bottom_half = image[height // 2:, :]
            gray = cv2.cvtColor(bottom_half, cv2.COLOR_BGR2GRAY)
            extracted_text = pytesseract.image_to_data(gray, output_type=pytesseract.Output.DICT)

            for i, text in enumerate(extracted_text["text"]):
                if "Show" in text or "More" in text:
                    x, y, w, h = (
                        extracted_text["left"][i],
                        extracted_text["top"][i] + height // 2,
                        extracted_text["width"][i],
                        extracted_text["height"][i],
                    )
                    screen_width, screen_height = pyautogui.size()
                    screen_x = int(x * (screen_width / width)) + 30
                    screen_y = int(y * (screen_height / height)) + 50
                    print(f"✅ 'Show More' button detected at ({screen_x}, {screen_y}). Clicking...")
                    pyautogui.moveTo(screen_x, screen_y, duration=random.uniform(0.5, 1.5))
                    pyautogui.click()
                    time.sleep(random.uniform(1.2, 2))
                    return
            print("⚠️ 'Show More' button not detected.")
        except Exception as e:
            print(f"⚠️ Error detecting 'Show More' button: {e}")

    def close_popup(self):
        print("🔍 Closing pop-up...")
        pyautogui.moveTo(900, 280, duration=random.uniform(0.3, 0.7))
        pyautogui.click()
        time.sleep(random.uniform(1, 1.5))

    def scroll_into_view(self, element):
        self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
        time.sleep(random.uniform(0.3, 0.8))

    def save_to_json(self):
        with open("glassdoor_jobs.json", "w", encoding="utf-8") as f:
            json.dump(self.jobs_data, f, indent=4, ensure_ascii=False)
        print(f"✅ Scraped {len(self.jobs_data)} jobs and saved.")

    def run(self):
        self.open_glassdoor()
        self.scroll_slowly()
        self.find_and_click_jobs()
        self.save_to_json()
        self.driver.quit()

if __name__ == "__main__":
    scraper = GlassdoorScraper("https://www.glassdoor.com/Job/jobs.htm?sc.keyword=Software%20Engineer")
    scraper.run()
