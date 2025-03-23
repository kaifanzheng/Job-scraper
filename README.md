# Glassdoor Job Scraper (OCR + GUI Automation)

This is a Python-based web scraper that extracts job listings and full descriptions from [Glassdoor](https://glassdoor.com) using screenshots, OCR, and GUI automation — mimicking human interaction to overcome dynamic content and bot protection.

## What This Scraper Does

- Loads a Glassdoor job search results page
- Visually detects and clicks the “Show more jobs” button
- Scrolls the page to reveal more listings
- Opens each job card to view the details
- Scrolls through full job descriptions and extracts all text
- Saves the result to a JSON file

## How It Works

This scraper does not rely on scraping HTML. Instead, it works visually, just like a human:

### OCR Detection via Screenshot

- Takes in-memory browser screenshots
- Uses `pytesseract` to detect text like "Show more jobs" or "Show more"
- Converts image coordinates to screen positions for clicking

### Mouse + Scroll Automation

- Uses `pyautogui` to:
  - Move the cursor like a human
  - Click visually-detected buttons
  - Scroll through job details naturally

### Browser Handling

- Uses `selenium` to open and navigate the page
- Captures browser-rendered content as PNGs for OCR analysis

## Why Use Screenshots Instead of Parsing HTML?

### Traditional scraping doesn't work well on Glassdoor:

- Content is often:
  - Loaded dynamically via JavaScript
  - Hidden inside shadow DOMs or React trees
  - Designed to block automated bots

### Screenshots + OCR solve this by:

- Working on exactly what the user sees
- Clicking buttons or detecting content visually
- Avoiding fragile CSS selectors and brittle DOM scraping

## Challenges Solved

- Detecting "Show more jobs" without relying on HTML tags
- Clicking content that isn’t accessible through the DOM
- Handling unpredictable UI behavior and modals like "Never Miss an Opportunity"
- Mimicking real-user behavior to avoid bot detection

## Requirements

- Python 3.7+
- Google Chrome installed
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) installed and added to your system path

Install dependencies:

```bash
pip install -r requirements.txt
```

## How to Run

```bash
python glassdoor_scraper.py
```

You can change the search keyword in the script:

```python
scraper = GlassdoorScraper("https://www.glassdoor.com/Job/jobs.htm?sc.keyword=Software%20Engineer")
```

## Output

Results are saved in:

```
glassdoor_jobs.json
```

Each job is stored like:

```json
{
  "job_details": "Full text of the job description..."
}
```

## Disclaimer

This tool is for personal, educational, and research use only.  
Please respect [Glassdoor’s Terms of Service](https://www.glassdoor.com/about/terms.htm).
