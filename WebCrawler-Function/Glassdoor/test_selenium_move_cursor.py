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
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from PIL import Image
import io

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
            
    def click_show_more_jobs(self, screenshot_path, debug=False):
        """Use OCR to detect and click the 'Show more jobs' button."""
        try:
            image = cv2.imread(screenshot_path)
            if image is None:
                print("⚠️ Error: Unable to load the screenshot.")
                return

            height, width, _ = image.shape
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            # OCR with detailed output
            extracted = pytesseract.image_to_data(gray, output_type=pytesseract.Output.DICT)

            # Combine nearby words into phrases
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

                # Add current token
                current_text += " " + text
                current_coords.append((
                    extracted["left"][i],
                    extracted["top"][i],
                    extracted["width"][i],
                    extracted["height"][i]
                ))

                # If next word is far or last word, finalize group
                if (i + 1 >= len(extracted["text"])) or extracted["text"][i + 1].strip() == "":
                    boxes.append((current_text.strip(), current_coords))
                    current_text = ""
                    current_coords = []

            for text, coords in boxes:
                if "show more jobs" in text:
                    print(f"✅ Detected text: '{text}'")
                    # Average coordinates for center
                    avg_x = sum([x + w // 2 for x, y, w, h in coords]) // len(coords)
                    avg_y = sum([y + h // 2 for x, y, w, h in coords]) // len(coords)

                    screen_width, screen_height = pyautogui.size()
                    screen_x = int(avg_x * screen_width / width)
                    screen_y = int(avg_y * screen_height / height)

                    print(f"🖱 Clicking at ({screen_x}, {screen_y})")
                    pyautogui.moveTo(screen_x, screen_y+45, duration=random.uniform(0.4, 1.2))
                    pyautogui.click()
                    time.sleep(random.uniform(1.2, 2))

                    if debug:
                        for x, y, w, h in coords:
                            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
                        cv2.imwrite("debug_show_more_jobs_click.png", image)
                        print("🖼 Debug image saved: debug_show_more_jobs_click.png")
                    return

            print("⚠️ 'Show more jobs' button not detected.")

        except Exception as e:
            print(f"⚠️ Error detecting 'Show more jobs' button: {e}")


    def load_more_jobs(self,max_click=3):
        click_counter = 0
        print("✅ starting to find click more jobs button!")
        while True:
            if click_counter >= max_click:
                self.close_popup()
                break
            pyautogui.moveTo(200, 400, duration=random.uniform(0.5, 1.5))
            time.sleep(random.uniform(0.5, 1.5))
            screenshot_path = f"screen_shot/find_show_more_jobs_{click_counter}.png"
            self.driver.save_screenshot(screenshot_path)
            time.sleep(1.2)
            image = Image.open(screenshot_path)
            extracted_text = pytesseract.image_to_string(image).strip()
            if "Show more jobs" in extracted_text:
                    self.click_show_more_jobs(screenshot_path)
                    #click if show more jobs button still there
                    screenshot_path = f"screen_shot/find_show_more_jobs_{click_counter}.png"
                    self.driver.save_screenshot(screenshot_path)
                    time.sleep(1.2)
                    image = Image.open(screenshot_path)
                    if "Show more jobs" in extracted_text:
                        continue
            if "Never Miss an Opportunity" in extracted_text:
                    self.close_popup()
                    continue
            pyautogui.scroll(-165)
            time.sleep(random.uniform(0.5, 1.5))
            click_counter = click_counter + 1
        return
        
        

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
                self.click_show_more()
                showmore_button_counter += 1
                continue
            if "Never Miss an Opportunity" in extracted_text:
                self.close_popup()
                continue

            pyautogui.scroll(-7)
            time.sleep(random.uniform(1.2, 2))
            screenshot_counter += 1

        return "\n".join(full_text)


    def take_screenshot_from_driver(self):
        """Takes a screenshot using Selenium and returns it as a CV2 image."""
        png = self.driver.get_screenshot_as_png()
        image = Image.open(io.BytesIO(png)).convert("RGB")
        return cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

    def inject_cursor_js(self):
        js_code = """
            if (!window.fakeCursor) {
                const cursor = document.createElement('div');
                cursor.id = 'fakeCursor';
                cursor.style.position = 'fixed';
                cursor.style.width = '20px';
                cursor.style.height = '20px';
                cursor.style.border = '2px solid red';
                cursor.style.borderRadius = '50%';
                cursor.style.zIndex = '999999';
                cursor.style.pointerEvents = 'none';
                cursor.style.transition = 'top 0.3s, left 0.3s';
                document.body.appendChild(cursor);
                window.fakeCursor = cursor;
            }
        """
        self.driver.execute_script(js_code)

    def move_fake_cursor_and_click(self, x, y):
        js_code = f"""
            if (window.fakeCursor) {{
                fakeCursor.style.left = '{x - 10}px';
                fakeCursor.style.top = '{y - 10}px';
            }}

            const elem = document.elementFromPoint({x}, {y});
            if (elem) {{
                elem.click();
            }}
        """
        self.driver.execute_script(js_code)

    def click_show_more(self, max_scroll_attempts=3):
        self.inject_cursor_js()

        for scroll_attempt in range(max_scroll_attempts):
            print(f"🔄 Attempt {scroll_attempt + 1}/{max_scroll_attempts}")

            image = self.take_screenshot_from_driver()
            if image is None:
                print("⚠️ Error: Unable to load screenshot from driver.")
                return

            height, width, _ = image.shape
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            extracted_text = pytesseract.image_to_data(gray, output_type=pytesseract.Output.DICT)

            scroll_y = self.driver.execute_script("return window.pageYOffset;")
            print(f"🌀 Page scroll offset: {scroll_y}")

            for i, text in enumerate(extracted_text["text"]):
                text_clean = text.lower().replace(" ", "")
                if "showmore" in text_clean or ("show" in text_clean and "more" in text_clean):
                    x, y, w, h = (
                        extracted_text["left"][i],
                        extracted_text["top"][i],
                        extracted_text["width"][i],
                        extracted_text["height"][i],
                    )

                    center_x = x + w // 2
                    center_y = y + h // 2 - scroll_y

                    print(f"🎯 Found 'Show More' at image coords: x={x}, y={y}, w={w}, h={h}")
                    print(f"🖱️ Clicking via fake cursor at browser coords: ({center_x}, {center_y})")

                    # Draw red box for visual debug
                    cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 2)

                    self.move_fake_cursor_and_click(center_x, center_y)
                    time.sleep(random.uniform(1.2, 2))

                    debug_image_path = f"debug_show_more_attempt_{scroll_attempt + 1}.png"
                    cv2.imwrite(debug_image_path, image)
                    print(f"📸 Debug image saved: {debug_image_path}")
                    return

            # Save image anyway if not found
            debug_image_path = f"debug_show_more_attempt_{scroll_attempt + 1}_nofind.png"
            cv2.imwrite(debug_image_path, image)
            print(f"📸 No match. Debug image saved: {debug_image_path}")

            # Scroll and retry
            self.driver.execute_script("window.scrollBy(0, 300);")
            time.sleep(1)

        print("⚠️ 'Show More' button not detected after all attempts.")



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
