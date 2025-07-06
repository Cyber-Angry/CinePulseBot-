import os
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
BOT_OWNER_ID = "7298989448"
                                                                                 LOGS_DIR = "logs"
USERS_FILE = os.path.join(LOGS_DIR, "users.txt")
BLOCKED_FILE = os.path.join(LOGS_DIR, "blocked.txt")

os.makedirs(LOGS_DIR, exist_ok=True)
for f in [USERS_FILE, BLOCKED_FILE]:
    if not os.path.exists(f):
        open(f, "a").close()
                                                                                 def fetch_user_name(user_id):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/getChat?chat_id={user_id}"
        response = requests.get(url).json()
        if response.get("ok"):
            user = response["result"]
            if user.get("username"):
                return f"@{user['username']}"
            name = f"{user.get('first_name', '')} {user.get('last_name', '')}".strip()
            return name or f"User {user_id}"
    except:
        pass
    return f"User {user_id}"

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_user.id) != BOT_OWNER_ID:
        return
    buttons = [
        [InlineKeyboardButton("👥 View Total Users", callback_data="show_users")],                                                                                        [InlineKeyboardButton("🚫 View Blocked Users", callback_data="show_blocked")],                                                                                    [InlineKeyboardButton("✅ View Unblocked Users", callback_data="show_unblocked")]                                                                             ]
    await update.message.reply_text("👑 <b>Admin Panel</b>", parse_mode="HTML", reply_markup=InlineKeyboardMarkup(buttons))                                       
async def handle_admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if str(query.from_user.id) != BOT_OWNER_ID:
        return

    data = query.data

    with open(USERS_FILE, "r") as f:
        users = list(set(f.read().splitlines()))
    with open(BLOCKED_FILE, "r") as f:
        blocked = set(f.read().splitlines())

    if data == "show_users":
        msg = f"👥 <b>Total Users: {len(users)}</b>\n\n"
        buttons = []
        for i, uid in enumerate(users, 1):
            name = fetch_user_name(uid)
            is_blocked = uid in blocked
            label = f"{i}. {name} ({uid})"
            action = "Unblock" if is_blocked else "Block"
            callback = f"toggle:{uid}:{'unblock' if is_blocked else 'block'}"
            buttons.append([InlineKeyboardButton(action, callback_data=callback)])
            msg += f"{label}\n"
        await query.edit_message_text(msg, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(buttons))

    elif data == "show_blocked":
        msg = f"🚫 <b>Blocked Users: {len(blocked)}</b>\n\n"
        buttons = []
        for i, uid in enumerate(blocked, 1):
            name = fetch_user_name(uid)
            label = f"{i}. {name} ({uid})"
            callback = f"toggle:{uid}:unblock"
            buttons.append([InlineKeyboardButton("Unblock", callback_data=callback)])
            msg += f"{label}\n"
        await query.edit_message_text(msg, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(buttons))

    elif data == "show_unblocked":
        unblocked = [uid for uid in users if uid not in blocked]
        msg = f"✅ <b>Unblocked Users: {len(unblocked)}</b>\n\n"
        buttons = []
        for i, uid in enumerate(unblocked, 1):
            name = fetch_user_name(uid)
            label = f"{i}. {name} ({uid})"
            callback = f"toggle:{uid}:block"
            buttons.append([InlineKeyboardButton("Block", callback_data=callback)])                                                                                           msg += f"{label}\n"
        await query.edit_message_text(msg, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(buttons))
                                                                                     elif data.startswith("toggle"):
        _, uid, action = data.split(":")
        if action == "block":
            with open(BLOCKED_FILE, "a") as f:
                f.write(uid + "\n")
            await query.edit_message_text(f"✅ Blocked user {uid}")
        elif action == "unblock":
            with open(BLOCKED_FILE, "r") as f:
                lines = f.read().splitlines()
            with open(BLOCKED_FILE, "w") as f:
                for line in lines:                                                                   if line != uid:
                        f.write(line + "\n")
            await query.edit_message_text(f"✅ Unblocked user {uid}")

# ✅ Direct User ID blocking/unblocking from owner message
async def handle_admin_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_user.id) != BOT_OWNER_ID:
        return
    user_id = update.message.text.strip()
    if not user_id.isdigit():
        await update.message.reply_text("❌ Invalid User ID.")
        return

    with open(BLOCKED_FILE, "r") as f:
        blocked = set(f.read().splitlines())

    if user_id in blocked:                                                               blocked.remove(user_id)
        with open(BLOCKED_FILE, "w") as f:
            f.write("\n".join(blocked) + "\n")
        await update.message.reply_text(f"✅ Unblocked {user_id}")
    else:
        with open(BLOCKED_FILE, "a") as f:
            f.write(user_id + "\n")
        await update.message.reply_text(f"✅ Blocked {user_id}")