import time
import json
import random
import pytesseract
pytesseract.pytesseract.tesseract_cmd = "/opt/homebrew/bin/tesseract"
import pyautogui
import cv2
import numpy as np
import io
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

    def click_show_more_jobs(self, screenshot_bytes, debug=False):
        """Use OCR to detect and click the 'Show more jobs' button."""
        try:
            image = Image.open(io.BytesIO(screenshot_bytes))
            image_np = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            del image

            height, width, _ = image_np.shape
            gray = cv2.cvtColor(image_np, cv2.COLOR_BGR2GRAY)
            extracted = pytesseract.image_to_data(gray, output_type=pytesseract.Output.DICT)

            boxes = []
            current_text = ""
            current_coords = []

            for i in range(len(extracted["text"])):
                text = extracted["text"][i].strip().lower()
                conf = int(extracted["conf"][i])
                if conf < 60 or not text:
                    if current_text:
                        boxes.append((current_text.strip(), current_coords))
                        current_text = ""
                        current_coords = []
                    continue
                current_text += " " + text
                current_coords.append((
                    extracted["left"][i],
                    extracted["top"][i],
                    extracted["width"][i],
                    extracted["height"][i]
                ))
                if (i + 1 >= len(extracted["text"])) or extracted["text"][i + 1].strip() == "":
                    boxes.append((current_text.strip(), current_coords))
                    current_text = ""
                    current_coords = []

            for text, coords in boxes:
                if "show more jobs" in text:
                    print(f"✅ Detected text: '{text}'")
                    avg_x = sum([x + w // 2 for x, y, w, h in coords]) // len(coords)
                    avg_y = sum([y + h // 2 for x, y, w, h in coords]) // len(coords)
                    screen_width, screen_height = pyautogui.size()
                    screen_x = int(avg_x * screen_width / width)
                    screen_y = int(avg_y * screen_height / height)
                    print(f"🖱 Clicking at ({screen_x}, {screen_y})")
                    pyautogui.moveTo(screen_x, screen_y + 45, duration=random.uniform(0.4, 1.2))
                    pyautogui.click()
                    time.sleep(random.uniform(1.2, 2))
                    return
            print("⚠️ 'Show more jobs' button not detected.")
        except Exception as e:
            print(f"⚠️ Error detecting 'Show more jobs' button: {e}")

    def load_more_jobs(self, max_click=5):
        click_counter = 0
        print("✅ Starting to find 'Show more jobs' button...")

        while True:
            print("---------click counter: ",click_counter)
            if click_counter >= max_click:
                self.close_popup()
                break

            pyautogui.moveTo(200, 400, duration=random.uniform(0.5, 1.5))
            time.sleep(random.uniform(0.5, 1.5))

            screenshot_bytes = self.driver.get_screenshot_as_png()
            image = Image.open(io.BytesIO(screenshot_bytes))
            extracted_text = pytesseract.image_to_string(image).strip()
            del image
            if "Never Miss an Opportunity" in extracted_text:
                self.close_popup()
                continue
            if "Show more jobs" in extracted_text:
                print("🟩 'Show more jobs' detected. Attempting click...")
                self.click_show_more_jobs(screenshot_bytes)
                time.sleep(1.2)

                original_x, original_y = pyautogui.position()

                screenshot_bytes = self.driver.get_screenshot_as_png()
                image = Image.open(io.BytesIO(screenshot_bytes))
                recheck_text = pytesseract.image_to_string(image).strip()
                del image
                if "Never Miss an Opportunity" in recheck_text:
                    self.close_popup()
                    continue

                if "Show more jobs" in recheck_text:
                    for offset_y in [-5, 5, -10, 10, -15, 15,-20,20]:
                        pyautogui.moveTo(original_x, original_y + offset_y, duration=0.3)
                        pyautogui.click()
                        time.sleep(1.2)

                    screenshot_bytes = self.driver.get_screenshot_as_png()
                    image = Image.open(io.BytesIO(screenshot_bytes))
                    final_check_text = pytesseract.image_to_string(image).strip()
                    del image

                    if "Show more jobs" in final_check_text:
                        print("⛔ Still visible after retries. Breaking.")
                        break

            pyautogui.scroll(-165)
            time.sleep(random.uniform(0.5, 1.5))
            click_counter += 1

    def find_and_click_jobs(self):
        print("🔍 Scanning job listings...")
        job_list = self.driver.find_elements(By.CSS_SELECTOR, "li[data-test='jobListing']")
        print(f"✅ Found {len(job_list)} jobs.")

        for index, job in enumerate(job_list):
            try:
                self.scroll_into_view(job)
                time.sleep(random.uniform(2, 4))
                job.click()
                time.sleep(random.uniform(3, 6))
                job_text = self.extract_full_job_details(index)
                print(f"\n📌 Job {index + 1} Details:\n{job_text[:200]}...\n")
                self.jobs_data.append({"job_details": job_text})
            except Exception as e:
                print(f"⚠️ Error interacting with job: {e}")

    def extract_full_job_details(self, job_index):
        full_text = []
        screenshot_counter = 1
        showmore_button_counter = 0

        while True:
            screenshot_bytes = self.driver.get_screenshot_as_png()
            image = Image.open(io.BytesIO(screenshot_bytes))
            extracted_text = pytesseract.image_to_string(image).strip()
            del image

            if extracted_text:
                full_text.append(extracted_text)
                print(f"📸 Screenshot {screenshot_counter} - Extracted: {extracted_text[:60]}")

            if "Showless" in extracted_text or screenshot_counter >= 5 or showmore_button_counter >= 2:
                break
            if "Showmore" in extracted_text or "Show" in extracted_text or "More" in extracted_text:
                self.click_show_more(screenshot_bytes)
                showmore_button_counter += 1
                continue
            if "Never Miss an Opportunity" in extracted_text:
                self.close_popup()
                continue

            pyautogui.scroll(-10)
            time.sleep(random.uniform(1.2, 2))
            screenshot_counter += 1

        return "\n".join(full_text)

    def click_show_more(self, screenshot_bytes):
        offset_x = 30
        offset_y = 50
        try:
            # Load and convert screenshot to OpenCV format
            image = Image.open(io.BytesIO(screenshot_bytes))
            image_np = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            del image

            height, width, _ = image_np.shape

            # Focus only on bottom half
            bottom_half = image_np[height // 2:, :]
            gray = cv2.cvtColor(bottom_half, cv2.COLOR_BGR2GRAY)

            # OCR
            extracted = pytesseract.image_to_data(gray, output_type=pytesseract.Output.DICT)

            for i, text in enumerate(extracted["text"]):
                text = text.strip().lower()
                if "show" in text or "more" in text:
                    x = extracted["left"][i]
                    y = extracted["top"][i] + height // 2  # Adjust y for full image
                    w = extracted["width"][i]
                    h = extracted["height"][i]

                    screen_width, screen_height = pyautogui.size()
                    screen_x = int((x + w // 2) * screen_width / width) + offset_x
                    screen_y = int((y + h // 2) * screen_height / height) + offset_y

                    print(f"✅ 'Show More' button detected at ({screen_x}, {screen_y}). Clicking...")
                    pyautogui.moveTo(screen_x, screen_y, duration=random.uniform(0.4, 1.2))
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
        self.load_more_jobs()
        self.scroll_slowly()
        self.find_and_click_jobs()
        self.save_to_json()
        self.driver.quit()

if __name__ == "__main__":
    scraper = GlassdoorScraper("https://www.glassdoor.com/Job/jobs.htm?sc.keyword=Software%20Engineer")
    scraper.run()
