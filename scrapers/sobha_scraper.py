import requests
from bs4 import BeautifulSoup
from telegram_notifier import send_telegram_notification
from datetime import datetime

def scrape(url, project_data, today_str, headers):
    """Scrape Sobha website for new launches and update project data."""
    updated = False
    print(f"[DEBUG] Scraping Sobha: {url}")
    
    try:
        response = requests.get(url, timeout=10, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        project_divs = soup.find_all("div", class_="col-md-6 col-6 pr-md-5 mb-md-5 mb-4")
        print(f"[DEBUG] Found {len(project_divs)} Sobha project divs")

        for div in project_divs:
            name_tag = div.find("a", class_="d-flex")
            project_name = name_tag.get_text(strip=True) if name_tag else "Unnamed"
            print(f"[DEBUG] Sobha project name: {project_name}")

            image_link_tag = div.find("a", class_="d-block img-wrapper mb-4")
            project_url = image_link_tag["href"] if image_link_tag else "N/A"

            h3_tags = div.find_all("h3")
            meta_info = " | ".join(tag.get_text(strip=True) for tag in h3_tags) if h3_tags else ""

            new_launch_tag = div.find("span", class_="ml-auto units", string="New Launch")

            if new_launch_tag:
                if project_name not in project_data or (datetime.strptime(today_str, "%Y-%m-%d") - datetime.strptime(project_data[project_name]["date_found"], "%Y-%m-%d")).days <= 90:
                    print(f"\n⚠️  [NEW LAUNCH] {project_name} — {project_url}")
                    print(f"📍 {meta_info}")

                    previous_message_id = project_data.get(project_name, {}).get("message_id")
                    new_message_id = send_telegram_notification(
                        project_name, project_url, meta_info, previous_message_id
                    )

                    if new_message_id:
                        project_data[project_name] = {
                            "url": project_url,
                            "meta": meta_info,
                            "date_found": today_str,
                            "message_id": new_message_id
                        }
                        updated = True
            else:
                print(f"[DEBUG] No 'New Launch' tag for Sobha project: {project_name}")

    except Exception as e:
        print(f"[⚠️] Error scraping Sobha {url}: {e}")
        print(f"[DEBUG] Exception details: {type(e).__name__} - {str(e)}")

    return project_data, updated