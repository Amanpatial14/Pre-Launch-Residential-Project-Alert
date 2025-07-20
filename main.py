import os
import json
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from config import PROJECT_URLS, DATA_FILE, DATE_FORMAT
from scrapers.sobha_scraper import scrape as sobha_scrape
from scrapers.godrej_scraper import scrape as godrej_scrape
from scrapers.lntrealty_scraper import scrape as lntrealty_scrape
from scrapers.assetz_scraper import scrape as assetz_scrape

def load_project_data():
    """Load project data from local JSON file."""
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_project_data(data):
    """Save project data to local JSON file."""
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def scrape_and_notify():
    """Scrape project URLs, notify about new launches, and record data."""
    project_data = load_project_data()
    today_str = datetime.today().strftime(DATE_FORMAT)
    updated = False

    # Headers for Sobha requests
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive"
    }

    # Selenium setup for Godrej, L&T Realty, and Assetz
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-webgl")
    chrome_options.add_argument("--log-level=3")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    print("[🔍] Scraping websites...\n")

    for url in PROJECT_URLS:
        try:
            if "sobha.com" in url:
                project_data, was_updated = sobha_scrape(url, project_data, today_str, headers)
                updated |= was_updated
            elif "godrejproperties.com" in url:
                project_data, was_updated = godrej_scrape(url, project_data, today_str, driver)
                updated |= was_updated
            elif "lntrealty.com" in url:
                project_data, was_updated = lntrealty_scrape(url, project_data, today_str, driver)
                updated |= was_updated
            elif "assetzproperty.com" in url:
                project_data, was_updated = assetz_scrape(url, project_data, today_str, driver)
                updated |= was_updated
        except Exception as e:
            print(f"[⚠️] Error processing {url}: {e}")
            print(f"[DEBUG] Exception details: {type(e).__name__} - {str(e)}")

    driver.quit()  # Close Selenium driver
    if updated:
        save_project_data(project_data)
        print("\n[💾] Project history updated.")

    print(f"\n[✅] Done. Total tracked projects: {len(project_data)}")

if __name__ == "__main__":
    scrape_and_notify()