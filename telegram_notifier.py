# telegram_notifier.py

import requests
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_GROUP_ID

def delete_telegram_message(message_id):
    """Delete a Telegram message using its ID."""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/deleteMessage"
    payload = {
        "chat_id": TELEGRAM_GROUP_ID,
        "message_id": message_id
    }

    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print("[🗑️] Previous message deleted.")
        else:
            print(f"[⚠️] Could not delete message: {response.text}")
    except Exception as e:
        print(f"[❌] Error deleting message: {e}")

def send_telegram_notification(project_name, project_url, meta_info="", previous_message_id=None):
    """Send a Telegram message and delete the previous one if present."""
    
    # Delete previous message if exists
    if previous_message_id:
        delete_telegram_message(previous_message_id)

    # Prepare message
    message = f"🚨 *New Launch Detected!*\n🏗️ *{project_name}*\n🔗 {project_url}"
    if meta_info:
        message += f"\n📍 {meta_info}"

    # Send new message
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_GROUP_ID,
        "text": message,
        "parse_mode": "Markdown"
    }

    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print("[📬] Notification sent to Telegram.")
            return response.json()["result"]["message_id"]
        else:
            print(f"[⚠️] Telegram send error: {response.text}")
    except Exception as e:
        print(f"[❌] Telegram send failed: {e}")
    
    return None
