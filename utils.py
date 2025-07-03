import json
from telegram import ReplyKeyboardMarkup, KeyboardButton

# Link help note to add at the end of all content messages
LINK_HELP = (
    "\n\n⚠️ Link open nahi ho raha? Relax 😌\n"
    "👇 Ye dekhlo:\n"
    "💠 How to Open 🔗Link —\n"
    "https://t.me/cinepulsefam/31 ✅"
)

# Load data from a JSON file
def load_json(filename):
    with open(filename, "r", encoding="utf-8") as f:
        return json.load(f)

# Format a detailed message for selected item (title, description, episodes)
def format_item_message(title, description, episodes, quality):
    msg = f"<b>{title}</b>\n{description}\n\n"

    if not episodes:
        msg += "❌ No episodes available."
    else:
        for ep, link in episodes.items():
            msg += f"🔹 <b>{ep}</b> → <a href='{link}'>Download</a>\n"

    msg += LINK_HELP  # ⚠️ Just added this — nothing else touched
    return msg

# Build keyboard with items paginated 2 per row + nav buttons
def build_reply_keyboard(items, page, category=None):
    items_per_page = 30
    start = (page - 1) * items_per_page
    end = start + items_per_page
    page_items = items[start:end]

    keyboard = []
    row = []

    for i, item in enumerate(page_items, 1):
        btn_text = f"{item['title']} {item.get('emoji', '')}".strip()
        row.append(KeyboardButton(btn_text))
        if i % 2 == 0:
            keyboard.append(row)
            row = []

    if row:
        keyboard.append(row)

    # Navigation Row
    nav_buttons = []
    if page > 1:
        nav_buttons.append(KeyboardButton("⏮ Back"))
    nav_buttons.append(KeyboardButton("🏠 Main Menu"))
    if end < len(items):
        nav_buttons.append(KeyboardButton("⏭ Next"))

    keyboard.append(nav_buttons)

    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)