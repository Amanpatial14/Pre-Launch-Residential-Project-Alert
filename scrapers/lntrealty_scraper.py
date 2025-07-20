from bs4 import BeautifulSoup
from telegram_notifier import send_telegram_notification
from datetime import datetime

def scrape(url, project_data, today_str, driver):
    """Scrape L&T Realty website for new launches and update project data."""
    updated = False
    print(f"[DEBUG] Scraping L&T Realty: {url}")
    
    try:
        driver.get(url)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        project_divs = soup.find_all("div", class_="slider-gallery-item")
        print(f"[DEBUG] Found {len(project_divs)} L&T Realty project divs")

        for div in project_divs:
            desc_tag = div.find("div", class_="desc")
            project_name = "Unnamed"
            new_launch = False
            if desc_tag:
                name_tag = desc_tag.find("span", class_="project-location-span")
                project_name = name_tag.get_text(strip=True) if name_tag else "Unnamed"
                desc_text = desc_tag.get_text(strip=True).lower()
                new_launch = "(new launch)" in desc_text

            print(f"[DEBUG] L&T Realty project name: {project_name}")

            location_tag = div.find("div", class_="project-location")
            location = location_tag.get_text(strip=True) if location_tag else ""

            meta_info = location
            print(f"[DEBUG] L&T Realty meta info: {meta_info}")

            if new_launch:
                project_url = "N/A"
                link_tag = div.find("a", class_="lnt-btn")
                if link_tag and "href" in link_tag.attrs:
                    href = link_tag["href"]
                    project_url = f"https://www.lntrealty.com{href}" if href.startswith("/") else href
                print(f"[DEBUG] L&T Realty project URL: {project_url}")

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
                        print(f"[ERROR] Failed to send Telegram notification for L&T Realty project: {project_name}")
            else:
                print(f"[DEBUG] No 'New Launch' tag for L&T Realty project: {project_name}")

    except Exception as e:
        print(f"[⚠️] Error scraping L&T Realty {url}: {e}")
        print(f"[DEBUG] Exception details: {type(e).__name__} - {str(e)}")

    return project_data, updated