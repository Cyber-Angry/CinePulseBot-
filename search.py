from difflib import get_close_matches
from telegram import Update
from telegram.ext import ContextTypes
import os
import json
from user_logger import handle_bot_block

# ✅ JSON files to search in
DATA_FILES = [
    "anime_data.json",
    "kdrama_data.json",
    "bollywood_data.json",
    "marvel_data.json",
    "hollywood_data.json",
    "series_data.json",
    "latest_data.json",
    "eighteenplus_data.json",
]

# ✅ Convert poster URLs properly
def fix_poster_url(url: str) -> str:
    if not url:
        return ""
    if url.endswith((".jpg", ".jpeg", ".png", ".webp")) or "i.ibb.co" in url:
        return url
    if "ibb.co/" in url:
        code = url.strip().split("/")[-1]
        return f"https://i.ibb.co/{code}/poster.jpg"
    if "catbox.moe" in url:
        return url.replace("https://catbox.moe/", "https://files.catbox.moe/")
    return url

# ✅ Combine all data from all JSON files
def load_all_data():
    all_data = {}
    for file in DATA_FILES:
        if os.path.exists(file):
            try:
                with open(file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    all_data.update(data)
            except Exception as e:
                print(f"[❌] Failed to load {file}: {e}")
    return all_data

# ✅ Used in bot.py → search_movie(query)
def search_movie(query):
    data = load_all_data()
    matches = get_close_matches(query, list(data.keys()), n=1, cutoff=0.3)

    if not matches:
        return None

    title = matches[0]
    item = data[title]
    poster = fix_poster_url(item.get("poster", ""))
    audio = item.get("audio", "Hindi + English")
    imdb = item.get("imdb", "N/A")
    links = "\n".join(item.get("links", []))

    # Base caption
    base = f"<b>{title}</b>\n⭐ IMDb: {imdb}\n🔊 Audio: {audio}\n\n"
    footer = "\n\n⚠️ Link not opening?\n🔗 How to Open — https://t.me/cinepulsefam/31"

    # ✅ Limit caption to 1024 characters
    body = links
    total = base + body + footer
    if len(total) > 1024:
        allowed_links = 1024 - len(base) - len(footer) - 50
        body = links[:allowed_links] + "\n🔗 More links available..."
        total = base + body + footer

    return title, poster, total

# ✅ When user types something to search
async def search_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    query = update.message.text.strip()

    if not query:
        await update.message.reply_text("❌ Please enter something to search.")
        return

    result = search_movie(query)
    if not result:
        await update.message.reply_text("❌ No results found. Try a different name.")
        return

    title, poster, caption = result

    try:
        if poster:
            await update.message.reply_photo(photo=poster, caption=caption, parse_mode="HTML")
        else:
            await update.message.reply_text(caption, parse_mode="HTML")
    except Exception as e:
        err = str(e).lower()
        print(f"[❗] Search error: {e}")
        if "forbidden" in err or "bot was blocked" in err or "unauthorized" in err:
            handle_bot_block(user_id)

        await update.message.reply_text(caption[:4000], parse_mode="HTML")
