from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
from utils import load_json

# Load Latest data
latest_data = load_json("latest_data.json")

# Show Latest Releases in 15x2 layout
async def show_latest(update: Update, context: ContextTypes.DEFAULT_TYPE, page=1):
    context.user_data["latest_page"] = page
    items = [{"title": title, "emoji": latest_data[title].get("emoji", "")} for title in latest_data]
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

    await update.message.reply_text("✨🎬 𝐋𝐚𝐭𝐞𝐬𝐭 𝐑𝐞𝐥𝐞𝐚𝐬𝐞𝐬", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))

# Handle Latest selection
async def handle_latest_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    page = context.user_data.get("latest_page", 1)
    items = [{"title": title, "emoji": latest_data[title].get("emoji", "")} for title in latest_data]
    total_pages = (len(items) - 1) // 30 + 1

    # Navigation
    if text == "⏮ Back":
        if page > 1:
            await show_latest(update, context, page - 1)
        else:
            await update.message.reply_text("❌ Already at first page.")
        return

    elif text == "⏭ Next":
        if page < total_pages:
            await show_latest(update, context, page + 1)
        else:
            await update.message.reply_text("❌ No more pages.")
        return

    elif text == "🏠 Main Menu":
        from bot import reply_markup
        await update.message.reply_text("🏠 Back to Main Menu:", reply_markup=reply_markup)
        return

    # Title match
    for title in latest_data:
        expected_btn = f"{title} {latest_data[title].get('emoji', '')}".strip()
        if text == expected_btn:
            data = latest_data[title]
            poster = data.get("poster", "")
            links = "\n".join(data.get("links", []))
            audio = "Hindi + Multi Audio"

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