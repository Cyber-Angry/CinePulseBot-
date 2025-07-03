from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
from utils import load_json

# Load K-Drama data
kdrama_data = load_json("kdrama_data.json")

# Show K-Drama titles with 15x2 button layout
async def show_kdrama(update: Update, context: ContextTypes.DEFAULT_TYPE, page=1):
    context.user_data["kdrama_page"] = page
    items = [{"title": title, "emoji": kdrama_data[title].get("emoji", "")} for title in kdrama_data]
    total_items = len(items)
    total_pages = (total_items - 1) // 30 + 1

    if page < 1 or page > total_pages:
        await update.message.reply_text("❌ No more pages.")
        return

    start = (page - 1) * 30
    end = start + 30
    current_items = items[start:end]

    # 15x2 button layout
    keyboard = []
    for i in range(0, len(current_items), 2):
        left = current_items[i]
        right = current_items[i + 1] if i + 1 < len(current_items) else None
        row = [f"{left['title']} {left['emoji']}".strip()]
        if right:
            row.append(f"{right['title']} {right['emoji']}".strip())
        keyboard.append(row)

    keyboard.append(["⏮ Back", "⏭ Next"])
    keyboard.append(["🏠 Main Menu"])

    await update.message.reply_text("🎬 Choose a K-Drama:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))

# Handle K-Drama selection
async def handle_kdrama_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    page = context.user_data.get("kdrama_page", 1)
    items = [{"title": title, "emoji": kdrama_data[title].get("emoji", "")} for title in kdrama_data]
    total_pages = (len(items) - 1) // 30 + 1

    if text == "⏮ Back":
        if page > 1:
            await show_kdrama(update, context, page - 1)
        else:
            await update.message.reply_text("❌ Already at first page.")
        return

    elif text == "⏭ Next":
        if page < total_pages:
            await show_kdrama(update, context, page + 1)
        else:
            await update.message.reply_text("❌ No more pages.")
        return

    elif text == "🏠 Main Menu":
        from bot import reply_markup
        await update.message.reply_text("🏠 Back to Main Menu:", reply_markup=reply_markup)
        return

    # Show K-Drama details
    for title in kdrama_data:
        expected_btn = f"{title} {kdrama_data[title].get('emoji', '')}".strip()
        if text == expected_btn:
            data = kdrama_data[title]
            poster = data.get("poster", "")
            links = "\n".join(data.get("links", []))

            # Link help message
            link_help = (
                "\n\n⚠️ Link open nahi ho raha? Relax 😌\n"
                "👇 Ye dekhlo:\n"
                "💠 How to Open 🔗Link —\n"
                "https://t.me/cinepulsefam/31 ✅"
            )

            caption = f"<b>{title}</b>\n\n🔊 Audio: Hindi + Korean\n\n{links}{link_help}"

            if poster:
                if len(caption) > 1024:
                    await update.message.reply_photo(photo=poster)
                    await update.message.reply_text(caption, parse_mode="HTML")
                else:
                    await update.message.reply_photo(photo=poster, caption=caption, parse_mode="HTML")
            else:
                await update.message.reply_text(caption, parse_mode="HTML")
            return

    await update.message.reply_text("❌ Invalid option. Please use the menu.")