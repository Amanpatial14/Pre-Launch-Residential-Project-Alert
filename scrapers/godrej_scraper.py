from bs4 import BeautifulSoup
from telegram_notifier import send_telegram_notification
from datetime import datetime

def scrape(url, project_data, today_str, driver):
    """Scrape Godrej website for new launches and update project data."""
    updated = False
    print(f"[DEBUG] Scraping Godrej: {url}")
    
    try:
        driver.get(url)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        project_divs = soup.find_all("div", class_="property-info")
        print(f"[DEBUG] Found {len(project_divs)} Godrej project divs")

        for div in project_divs:
            name_tag = div.find("h3")
            project_name = name_tag.get_text(strip=True) if name_tag else "Unnamed"
            print(f"[DEBUG] Godrej project name: {project_name}")

            location_tag = div.find("span", class_="uppercase")
            location = location_tag.get_text(strip=True) if location_tag else ""

            price_tag = div.find("span", class_="ml-1")
            price = price_tag.get_text(strip=True) if price_tag else ""

            bhk_tag = div.find("div", class_="mt-1")
            bhk = bhk_tag.get_text(strip=True) if bhk_tag and "BHK" in bhk_tag.get_text() else ""

            meta_info = " | ".join(filter(None, [location, price, bhk]))
            print(f"[DEBUG] Godrej meta info: {meta_info}")

            new_launch_tag = div.find(lambda tag: tag.name == "span" and "new launch" in tag.get_text(strip=True).lower())

            if new_launch_tag:
                project_url = "N/A"
                parent_a = div.find_parent("a")
                if parent_a and "href" in parent_a.attrs:
                    href = parent_a["href"]
                    project_url = f"https://www.godrejproperties.com{href}" if href.startswith("/") else href
                print(f"[DEBUG] Godrej project URL: {project_url}")

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
                        print(f"[ERROR] Failed to send Telegram notification for Godrej project: {project_name}")
            else:
                print(f"[DEBUG] No 'New Launch' tag for Godrej project: {project_name}")

    except Exception as e:
        print(f"[⚠️] Error scraping Godrej {url}: {e}")
        print(f"[DEBUG] Exception details: {type(e).__name__} - {str(e)}")

    return project_data, updated