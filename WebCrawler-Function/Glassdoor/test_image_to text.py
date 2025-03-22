import pytesseract
import pyautogui
import cv2

def click_show_more(screenshot_path):
        try:
            image = cv2.imread(screenshot_path)
            if image is None:
                print("⚠️ Error: Unable to load the screenshot.")
                return

            height, width, _ = image.shape
            bottom_half = image[height // 2:, :]
            gray = cv2.cvtColor(bottom_half, cv2.COLOR_BGR2GRAY)
            extracted_text = pytesseract.image_to_data(gray, output_type=pytesseract.Output.DICT)
            print(extracted_text)

            print("⚠️ 'Show More' button not detected.")
        except Exception as e:
            print(f"⚠️ Error detecting 'Show More' button: {e}")


click_show_more("/Users/kaifan/Desktop/linkedin-job-scraper/WebCrawler-Function/Glassdoor/screen_shot/find_show_more_jobs_4.png")