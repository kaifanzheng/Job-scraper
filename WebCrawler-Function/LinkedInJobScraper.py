from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time, random, json

class LinkedInJobScraper:
    def __init__(self, username, password, proxy=None):
        self.username = username
        self.password = password
        self.proxy = proxy
        self.driver = self.setup_driver()

    def setup_driver(self):
        """Sets up Chrome WebDriver with options for human-like behavior."""
        options = Options()
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.1 Safari/605.1.15",
        ]
        options.add_argument(f"user-agent={random.choice(user_agents)}")
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument("--start-maximized")
        
        if self.proxy:
            options.add_argument(f'--proxy-server={self.proxy}')
            
        return webdriver.Chrome(options=options)
    
    def login(self):
        try:
            # Setup Chrome options (e.g., for proxy)
            chrome_options = webdriver.ChromeOptions()
            if self.proxy:
                chrome_options.add_argument(f'--proxy-server={self.proxy}')
            # Initialize WebDriver (Chrome in this example) with options
            self.driver.get("https://www.linkedin.com/login")
            
            # Wait for the login form elements to load
            wait = WebDriverWait(self.driver, 10)
            username_field = wait.until(EC.element_to_be_clickable((By.ID, "username")))
            password_field = wait.until(EC.element_to_be_clickable((By.ID, "password")))
            
            # Type the username with human-like random delays
            for char in self.username:
                username_field.send_keys(char)
                time.sleep(random.uniform(0.1, 0.3))  # random delay between keystrokes
            
            # Type the password with human-like random delays
            for char in self.password:
                password_field.send_keys(char)
                time.sleep(random.uniform(0.1, 0.3))
            
            # Locate the Sign In button (using its type or text)
            sign_in_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']")))
            
            # Move mouse to the Sign In button before clicking (to simulate hover)
            actions = ActionChains(self.driver)
            actions.move_to_element(sign_in_btn).pause(random.uniform(0.2, 0.5)).click(sign_in_btn).perform()
            
            # Optionally, wait a moment for post-login page to load (or verify successful login)
            WebDriverWait(self.driver, 10).until(EC.url_contains("/feed"))  # waits until redirected to feed/home
        except Exception as e:
            # Handle any errors during login
            print(f"[ERROR] LinkedIn login failed: {e}")
            if self.driver:
                self.driver.quit()  # close the browser if it was opened
            raise  # re-raise the exception after cleanup, or return False as needed
        return self.driver  # return the logged-in WebDriver instance for further use
    
    
    def scrape_jobs(self):
        """Scrapes job details from LinkedIn recommended jobs and stores them as JSON."""
        self.driver.get("https://www.linkedin.com/jobs/collections/recommended/")
        time.sleep(random.uniform(3, 5))

        jobs_data = []
        original_window = self.driver.current_window_handle

        for page in range(1, 4):
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            for _ in range(5):
                self.driver.execute_script("window.scrollBy(0, 800);")
                time.sleep(random.uniform(1, 2))
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
            
            job_cards = self.driver.find_elements(By.CSS_SELECTOR, "li.jobs-search-results__list-item")
            for job_card in job_cards:
                try:
                    title_elem = job_card.find_element(By.CSS_SELECTOR, "a.job-card-list__title")
                    job_title = title_elem.text.strip()
                    job_url = title_elem.get_attribute("href")
                except:
                    job_title, job_url = None, None

                try:
                    company_elem = job_card.find_element(By.CSS_SELECTOR, "a.job-card-container__link")
                    company_name = company_elem.text.strip()
                except:
                    company_name = None

                try:
                    location_elem = job_card.find_element(By.CSS_SELECTOR, "li.job-card-container__metadata-item")
                    location = location_elem.text.strip()
                except:
                    location = None

                job_desc, skills_list = "", []
                if job_url:
                    self.driver.execute_script("window.open(arguments[0]);", job_url)
                    self.driver.switch_to.window(self.driver.window_handles[-1])
                    time.sleep(random.uniform(3, 6))

                    try:
                        see_more_btn = self.driver.find_element(By.XPATH, "//button[contains(text(), 'See more')]")
                        see_more_btn.click()
                        time.sleep(random.uniform(1, 2))
                    except:
                        pass

                    try:
                        desc_elem = self.driver.find_element(By.ID, "job-details")
                        job_desc = desc_elem.text.strip()
                    except:
                        job_desc = ""

                    try:
                        bullet_items = self.driver.find_elements(By.CSS_SELECTOR, "#job-details ul li")
                        skills_list = [item.text.strip() for item in bullet_items if item.text.strip()]
                    except:
                        skills_list = []

                    self.driver.close()
                    self.driver.switch_to.window(original_window)
                    time.sleep(random.uniform(2, 4))

                jobs_data.append({
                    "title": job_title,
                    "company": company_name,
                    "location": location,
                    "description": job_desc,
                    "skills": skills_list,
                    "url": job_url
                })

            try:
                next_page_btn = self.driver.find_element(By.XPATH, f"//button[@aria-label='Page {page+1}']")
                ActionChains(self.driver).move_to_element(next_page_btn).pause(random.uniform(0.2, 0.5)).click(next_page_btn).perform()
                time.sleep(random.uniform(3, 6))
            except:
                break

        with open("recommended_jobs.json", "w", encoding="utf-8") as f:
            json.dump(jobs_data, f, ensure_ascii=False, indent=4)
        print(f"Scraping complete. Collected {len(jobs_data)} jobs, saved to recommended_jobs.json")
        return jobs_data

    def close(self):
        """Closes the WebDriver session."""
        self.driver.quit()

if __name__ == "__main__":
    scraper = LinkedInJobScraper("zhengkaifan73@gmail.com", "zkf20001212")
    scraper.login()
    scraper.scrape_jobs()
    scraper.close()

