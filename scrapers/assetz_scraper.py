from bs4 import BeautifulSoup
from telegram_notifier import send_telegram_notification
from datetime import datetime

def scrape(url, project_data, today_str, driver):
    """Scrape Assetz Property website for new launches and update project data."""
    updated = False
    print(f"[DEBUG] Scraping Assetz Property: {url}")
    
    try:
        driver.get(url)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        project_divs = soup.find_all("div", class_="project_details_box")
        print(f"[DEBUG] Found {len(project_divs)} Assetz project divs")

        for div in project_divs:
            name_tag = div.find("h1", class_="fontsmuseo_bold")
            project_name = name_tag.find("span").get_text(strip=True) if name_tag and name_tag.find("span") else "Unnamed"
            print(f"[DEBUG] Assetz project name: {project_name}")

            new_launch_tag = div.find("div", class_="project_layer_img")
            new_launch = new_launch_tag and new_launch_tag.find("p", string="New Launch") is not None
            print(f"[DEBUG] Assetz new launch: {new_launch}")

            location_tag = div.find("p", class_=None)  # Last <p> tag with location
            location = location_tag.get_text(strip=True).replace("\n", " ") if location_tag else ""

            size_bhk_tag = div.find("h4")
            size_bhk = size_bhk_tag.get_text(strip=True).replace("\n", " ") if size_bhk_tag else ""

            price_tag = div.find("p", string=lambda text: text and "Crore" in text)
            price = price_tag.get_text(strip=True) if price_tag else ""

            meta_info = " | ".join(filter(None, [location, size_bhk, price]))
            print(f"[DEBUG] Assetz meta info: {meta_info}")

            link_tag = div.find("a", href=True)
            project_url = link_tag["href"] if link_tag else "N/A"
            print(f"[DEBUG] Assetz project URL: {project_url}")

            if new_launch:
                if project_name not in project_data or (datetime.strptime(today_str, "%Y-%m-%d") - datetime.strptime(project_data[project_name]["date_found"], "%Y-%m-%d")).days <= 30:
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
                        print(f"[ERROR] Failed to send Telegram notification for Assetz project: {project_name}")
            else:
                print(f"[DEBUG] No 'New Launch' tag for Assetz project: {project_name}")

    except Exception as e:
        print(f"[⚠️] Error scraping Assetz {url}: {e}")
        print(f"[DEBUG] Exception details: {type(e).__name__} - {str(e)}")

    return project_data, updated