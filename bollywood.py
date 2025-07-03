from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
from utils import load_json

# Load Bollywood movie data
bollywood_data = load_json("bollywood_data.json")

# Convert ibb.co to direct image URL
def convert_poster_url(poster: str) -> str:
    if poster.startswith("https://ibb.co/"):
        poster_id = poster.split("/")[-1]
        return f"https://i.ibb.co/{poster_id}.jpg"
    return poster

# Show Bollywood titles with 15x2 button layout
async def show_bollywood(update: Update, context: ContextTypes.DEFAULT_TYPE, page=1):
    context.user_data["bollywood_page"] = page
    items = [{"title": title, "emoji": bollywood_data[title].get("emoji", "")} for title in bollywood_data]
    total_items = len(items)
    total_pages = (total_items - 1) // 30 + 1

    if page < 1 or page > total_pages:
        await update.message.reply_text("❌ No more pages.")
        return

    start = (page - 1) * 30
    end = start + 30
    current_items = items[start:end]

    keyboard = []
    for i in range(0, len(current_items), 2):
        row = []
        left = current_items[i]
        row.append(f"{left['title']} {left['emoji']}".strip())
        if i + 1 < len(current_items):
            right = current_items[i + 1]
            row.append(f"{right['title']} {right['emoji']}".strip())
        keyboard.append(row)

    keyboard.append(["⏮ Back", "⏭ Next"])
    keyboard.append(["🏠 Main Menu"])

    await update.message.reply_text("📽️ Choose a Bollywood Movie:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))

# Handle Bollywood selection
async def handle_bollywood_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    page = context.user_data.get("bollywood_page", 1)
    items = [{"title": title, "emoji": bollywood_data[title].get("emoji", "")} for title in bollywood_data]
    total_pages = (len(items) - 1) // 30 + 1

    # Navigation
    if text == "⏮ Back":
        if page > 1:
            await show_bollywood(update, context, page - 1)
        else:
            await update.message.reply_text("❌ Already at first page.")
        return

    elif text == "⏭ Next":
        if page < total_pages:
            await show_bollywood(update, context, page + 1)
        else:
            await update.message.reply_text("❌ No more pages.")
        return

    elif text == "🏠 Main Menu":
        from bot import reply_markup
        await update.message.reply_text("🏠 Back to Main Menu:", reply_markup=reply_markup)
        return

    # Check for title match
    for title in bollywood_data:
        expected_btn = f"{title} {bollywood_data[title].get('emoji', '')}".strip()
        if text == expected_btn:
            data = bollywood_data[title]
            poster = convert_poster_url(data.get("poster", ""))
            links = "\n".join(data.get("links", []))
            audio = data.get("audio", "Hindi")

            link_help = (
                "\n\n⚠️ Link open nahi ho raha? Relax 😌\n"
                "👇 Ye dekhlo:\n"
                "💠 How to Open 🔗Link —\n"
                "https://t.me/cinepulsefam/31 ✅"
            )

            caption = f"<b>{title}</b>\n\n🔊 Audio: {audio}\n\n{links}{link_help}"

            try:
                if poster:
                    if len(caption) > 1024:
                        await update.message.reply_photo(photo=poster)
                        await update.message.reply_text(caption, parse_mode="HTML")
                    else:
                        await update.message.reply_photo(photo=poster, caption=caption, parse_mode="HTML")
                else:
                    await update.message.reply_text(caption, parse_mode="HTML")
            except Exception as e:
                print(f"[❗] Image error for {title}: {e}")
                await update.message.reply_text(caption, parse_mode="HTML")
            return

    await update.message.reply_text("❌ Invalid option. Please use the menu.")