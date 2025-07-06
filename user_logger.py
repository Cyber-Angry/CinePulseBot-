import os
import requests
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
BOT_OWNER_ID = "7298989448"

# 🔐 Ensure logs folder and required files exist
os.makedirs("logs", exist_ok=True)
for file in ["users.txt", "blocked.txt", "block_count.txt"]:
    path = f"logs/{file}"
    if not os.path.exists(path):
        open(path, "a").close()

USERS_FILE = "logs/users.txt"
BLOCKED_FILE = "logs/blocked.txt"
BLOCK_COUNT_FILE = "logs/block_count.txt"

# ✅ Log a new user
def log_user(user_id):
    user_id = str(user_id)
    if user_id == BOT_OWNER_ID:
        return
    with open(USERS_FILE, "r+") as f:
        users = f.read().splitlines()
        if user_id not in users:
            f.write(user_id + "\n")

# ✅ Check if user is banned
def is_banned(user_id):
    user_id = str(user_id)
    if user_id == BOT_OWNER_ID:
        return False
    with open(BLOCKED_FILE, "r") as f:
        return user_id in f.read().splitlines()

# ✅ Get user’s display name using Telegram API
def get_user_name(user_id):
    try:
        r = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getChat?chat_id={user_id}")
        data = r.json()
        if data.get("ok"):
            user = data["result"]
            name = f"{user.get('first_name', '')} {user.get('last_name', '')}".strip()
            if name:
                return name
            elif user.get("username"):
                return f"@{user['username']}"
    except Exception as e:
        print(f"Error fetching user name for {user_id}: {e}")
    return f"User {user_id}"

# ✅ Automatically block user after 3 warnings
def handle_bot_block(user_id):
    user_id = str(user_id)
    if user_id == BOT_OWNER_ID:
        return False

    counts = {}
    with open(BLOCK_COUNT_FILE, "r+") as f:
        lines = f.read().splitlines()
        for line in lines:
            if ":" in line:
                uid, count = line.split(":")
                counts[uid] = int(count)

    current_count = counts.get(user_id, 0) + 1
    counts[user_id] = current_count

    with open(BLOCK_COUNT_FILE, "w") as f:
        for uid, count in counts.items():
            f.write(f"{uid}:{count}\n")

    user_display = get_user_name(user_id)

    if current_count >= 3:
        with open(BLOCKED_FILE, "r+") as f:
            blocked = f.read().splitlines()
            if user_id not in blocked:
                f.write(user_id + "\n")
                print(f"🚫 Blocked {user_display}")
        return True

    print(f"⚠️ Warning {user_display} - {current_count}/3")
    return False