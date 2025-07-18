import os
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from telegram_notifier import send_telegram_notification
from config import PROJECT_URLS,DATA_FILE,DATE_FORMAT

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

def is_new_or_recent(project_name, data):
    """Check if project is new or launched within the last 30 days."""
    today = datetime.today()
    if project_name not in data:
        return True
    date_found = datetime.strptime(data[project_name]["date_found"], DATE_FORMAT)
    return (today - date_found).days <= 30

def scrape_and_notify():
    """Scrape project URLs, notify about new launches, and record data."""
    project_data = load_project_data()
    today_str = datetime.today().strftime(DATE_FORMAT)
    updated = False

    print("[🔍] Scraping Sobha websites...\n")

    for url in PROJECT_URLS:
        try:
            print(f"→ Scraping: {url}")
            response = requests.get(url, timeout=10)
            soup = BeautifulSoup(response.text, "html.parser")

            project_divs = soup.find_all("div", class_="col-md-6 col-6 pr-md-5 mb-md-5 mb-4")

            for div in project_divs:
                name_tag = div.find("a", class_="d-flex")
                project_name = name_tag.get_text(strip=True) if name_tag else "Unnamed"

                image_link_tag = div.find("a", class_="d-block img-wrapper mb-4")
                project_url = image_link_tag["href"] if image_link_tag else "N/A"

                h3_tags = div.find_all("h3")
                meta_info = " | ".join(tag.get_text(strip=True) for tag in h3_tags) if h3_tags else ""

                new_launch_tag = div.find("span", class_="ml-auto units", string="New Launch")

                if new_launch_tag:
                    if is_new_or_recent(project_name, project_data):
                        print(f"\n⚠️  [NEW LAUNCH] {project_name} — {project_url}")
                        print(f"📍 {meta_info}")

                        # Get previous message ID (if any)
                        previous_message_id = project_data.get(project_name, {}).get("message_id")

                        # Send notification
                        new_message_id = send_telegram_notification(
                            project_name, project_url, meta_info, previous_message_id
                        )

                        # Update JSON data
                        if new_message_id:
                            project_data[project_name] = {
                                "url": project_url,
                                "meta": meta_info,
                                "date_found": today_str,
                                "message_id": new_message_id
                            }
                            updated = True

        except Exception as e:
            print(f"[⚠️] Error scraping {url}: {e}")

    if updated:
        save_project_data(project_data)
        print("\n[💾] Project history updated.")

    print(f"\n[✅] Done. Total tracked projects: {len(project_data)}")

if __name__ == "__main__":
    scrape_and_notify()
