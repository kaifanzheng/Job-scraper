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
        """Logs into LinkedIn using the provided credentials."""
        try:
            self.driver.get("https://www.linkedin.com/login")

            # Wait for username and password fields
            wait = WebDriverWait(self.driver, 15)
            username_field = wait.until(EC.presence_of_element_located((By.ID, "username")))
            password_field = wait.until(EC.presence_of_element_located((By.ID, "password")))

            # Enter credentials with human-like typing delay
            for char in self.username:
                username_field.send_keys(char)
                time.sleep(random.uniform(0.1, 0.3))
            
            for char in self.password:
                password_field.send_keys(char)
                time.sleep(random.uniform(0.1, 0.3))

            # Click the Sign In button
            sign_in_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']")))
            ActionChains(self.driver).move_to_element(sign_in_btn).pause(random.uniform(0.2, 0.5)).click(sign_in_btn).perform()

            # **FIX**: Instead of waiting for the "/feed" URL, wait for the global navigation bar to load
            wait.until(EC.presence_of_element_located((By.ID, "global-nav")))
            print("✅ Login successful!")
            
        except Exception as e:
            print(f"[ERROR] LinkedIn login failed: {e}")
            self.driver.quit()
            raise

    
    def scroll_job_list(self):
        """Scroll down the job list to load all available jobs on the current page."""
        try:
            # Locate the scrollable job list container
            job_list_container = self.driver.find_element(By.CLASS_NAME, "jobs-search-results__list")
        except Exception:
            return  # If container not found (no jobs), exit
        prev_count = 0
        while True:
            # Scroll to the bottom of the container
            self.driver.execute_script("arguments[0].scrollTo(0, arguments[0].scrollHeight);", job_list_container)
            # Give time for new jobs to load
            time.sleep(1)
            jobs = self.driver.find_elements(By.CSS_SELECTOR, "li.jobs-search-results__list-item")
            count = len(jobs)
            if count == prev_count:
                # If no new jobs were loaded, we have reached the end of the list
                break
            prev_count = count

    def scrape_job_details(self):
        """Extract job details from the 'About the job' section after a job is clicked."""
        # Wait for the job title element in the right pane to be present (ensure job details loaded)
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "h2.jobs-unified-top-card__job-title"))
        )
        # 3. Extract job details: title, company, location, description, and skills
        title = self.driver.find_element(By.CSS_SELECTOR, "h2.jobs-unified-top-card__job-title").text.strip()
        # Company name might be in a span or anchor with the company name class
        try:
            company = self.driver.find_element(By.CSS_SELECTOR, "span.jobs-unified-top-card__company-name").text.strip()
        except Exception:
            try:
                company = self.driver.find_element(By.CSS_SELECTOR, "a.jobs-unified-top-card__company-name").text.strip()
            except Exception:
                company = ""
        # Location is often the first "bullet" element in the top card (may include workplace type)
        try:
            location = self.driver.find_element(By.CLASS_NAME, "jobs-unified-top-card__bullet").text.strip()
        except Exception:
            location = ""
        # Click "See more" in the description if available, to load full "About the job" text
        try:
            see_more_btn = self.driver.find_element(By.CLASS_NAME, "show-more-less-html__button")
            see_more_btn.click()
        except Exception:
            # If not found or clickable, skip (description might be short or already expanded)
            pass
        # Wait a brief moment for the full description to be visible after clicking "See more"
        time.sleep(0.5)
        # Now get the job description text from the "About the job" section
        try:
            desc_element = self.driver.find_element(By.CSS_SELECTOR, "div.show-more-less-html__markup")
            description = desc_element.text.strip()
        except Exception:
            description = ""
        # Extract skills from the description if they are listed as bullet points (as an example of "skills")
        skills = []
        try:
            # Find any list items in the description (common for skills/requirements lists)
            bullet_items = desc_element.find_elements(By.TAG_NAME, "li")
            for item in bullet_items:
                skill_text = item.text.strip()
                if skill_text:
                    skills.append(skill_text)
        except Exception:
            skills = []
        # Get current job URL (after clicking, the URL usually updates to the job's unique link)
        job_url = self.driver.current_url
        # Return all extracted info as a dictionary
        return {
            "title": title,
            "company": company,
            "location": location,
            "description": description,
            "skills": skills,
            "url": job_url
        }
    
    def scrape_all_jobs(self):
        """Scrape LinkedIn jobs from the given search URL, navigating all pages."""
        search_url = "https://www.linkedin.com/jobs/search/?keywords=Data%20Scientist&location=United%20States"
        # Initialize WebDriver (Chrome in this example)
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        # You might add options for headless browsing if needed, e.g.:
        # options.add_argument("--headless")
        driver = webdriver.Chrome(options=options)
        driver.get(search_url)
        all_jobs_data = []
        page_number = 1
        while True:
            # 1. Scroll down the job list to load all available jobs on this page
            self.scroll_job_list()
            # 2. Click on each job in the list to open its details and scrape information
            jobs = driver.find_elements(By.CSS_SELECTOR, "li.jobs-search-results__list-item")
            for job_elem in jobs:
                try:
                    # Scroll the job element into view and click it to load details
                    driver.execute_script("arguments[0].scrollIntoView();", job_elem)
                    job_elem.click()
                except Exception:
                    # Fallback clicking method if normal click fails (e.g., if element not in view)
                    driver.execute_script("arguments[0].click();", job_elem)
                # Implement proper waits to ensure elements are loaded before interaction
                job_data = self.scrape_job_details(driver)
                all_jobs_data.append(job_data)
            # 5. After scraping all jobs on the current page, navigate through pagination if 'Next' exists
            try:
                next_button = driver.find_element(By.XPATH, "//button[@aria-label='Next']")
            except Exception:
                next_button = None
            if next_button:
                # Check if the Next button is enabled or disabled
                if "disabled" in next_button.get_attribute("class") or not next_button.is_enabled():
                    # No further pages to scrape
                    break
                else:
                    page_number += 1
                    next_button.click()
                    # Wait for the new page of jobs to load (wait for the first job of the new page to be present or old jobs to be stale)
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "li.jobs-search-results__list-item"))
                    )
                    # Optionally, wait for staleness of an element from previous page to ensure page switch
                    # WebDriverWait(driver, 10).until(EC.staleness_of(jobs[0]))
                    # Continue loop to scrape next page
                    continue
            else:
                # No pagination (only one page of results)
                break
        # Close the browser after scraping all pages
        return all_jobs_data

    def close(self):
        """Closes the WebDriver session."""
        self.driver.quit()

if __name__ == "__main__":
    scraper = LinkedInJobScraper("zhengkaifan73@gmail.com", "zkf20001212")
    scraper.login()
    jobs = scraper.scrape_all_jobs()
    scraper.close()

    # 4. Store job information in JSON format (save to file or print out)
    with open("linkedin_jobs.json", "w", encoding="utf-8") as f:
        json.dump(jobs, f, ensure_ascii=False, indent=4)
    # Also print the JSON data to console (optional)
    print(json.dumps(jobs, ensure_ascii=False, indent=4))

