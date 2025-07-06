import time
import os
import requests
from user_logger import log_user, is_banned, handle_bot_block

BOT_OWNER_ID = 7298989448  # Replace with your real Telegram user ID

# Track user requests for DDoS detection
user_request_log = {}

# DDoS Settings
DDOS_REQUEST_LIMIT = 100
DDOS_TIME_WINDOW = 10  # seconds

def is_user_allowed(update) -> bool:
    user_id = update.effective_user.id

    # Allow owner always
    if user_id == BOT_OWNER_ID:
        return True

    # Banned?
    if is_banned(user_id):
        print(f"🚫 Blocked user tried: {user_id}")
        return False

    # Log user
    log_user(user_id)

    # Check flood/DDoS
    if detect_ddos(user_id):
        handle_bot_block(user_id)
        print(f"🚨 DDoS detected from {user_id}")
        return False

    return True

def detect_ddos(user_id: int) -> bool:
    if user_id == BOT_OWNER_ID:
        return False

    now = time.time()
    requests = user_request_log.get(user_id, [])
    requests = [t for t in requests if now - t < DDOS_TIME_WINDOW]
    requests.append(now)
    user_request_log[user_id] = requests

    return len(requests) > DDOS_REQUEST_LIMIT

# ✅ Get user name using Telegram API
def get_user_name(user_id):
    try:
        r = requests.get(f"https://api.telegram.org/bot{os.getenv('BOT_TOKEN')}/getChat?chat_id={user_id}")
        data = r.json()
        if data.get("ok"):
            user = data["result"]
            full_name = f"{user.get('first_name', '')} {user.get('last_name', '')}".strip()
            return full_name or "Unknown"
    except:
        pass
    return "Unknown"