import os
import logging
from dotenv import load_dotenv

from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ChatMemberStatus
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, filters
)

from user_logger import log_user, is_banned, handle_bot_block
from security import is_user_allowed
from howtouse import send_how_to_use
from request import handle_request
from search import search_movie

import latest, series, anime, kdrama, south, hollywood, bollywood, marvel, eighteenplus, multipart

# Load environment variables
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Channels for Force Join
FORCE_JOIN_CHANNELS = ["@oxAngry", "@modflux_99"]

# Setup logging
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO
)

# Main Menu Keyboard
menu_keyboard = [
    ["𝐋𝐚𝐭𝐞𝐬𝐭 𝐑𝐞𝐥𝐞𝐚𝐬𝐞𝐬 ✨🎞️"],
    ["𝐀𝐧𝐢𝐦𝐞 💀🔥", "𝐖𝐞𝐛𝐬𝐞𝐫𝐢𝐞𝐬 🎭📺"],
    ["𝐊-𝐃𝐫𝐚𝐦𝐚𝐬 💕✨", "𝐒𝐨𝐮𝐭𝐡 𝐌𝐨𝐯𝐢𝐞𝐬 💣🔥"],
    ["𝐇𝐨𝐥𝐥𝐲𝐰𝐨𝐨𝐝 🎬🌍", "𝐁𝐨𝐥𝐥𝐲𝐰𝐨𝐨𝐝 🌟🎥"],
    ["𝐌𝐚𝐫𝐯𝐞𝐥 + 𝐃𝐂 🦸‍♂️⚡", "𝟏𝟖+ 𝐂𝐨𝐧𝐭𝐞𝐧𝐭 🔞🔥"],
    ["𝗠𝘂𝗹𝘁𝗶-𝗣𝗮𝗿𝘁 𝗠𝗼𝘃𝗶𝗲𝘀 🎬"],
    ["𝐒𝐞𝐚𝐫𝐜𝐡 🔍🧠"],
    ["𝐇𝐨𝐰 𝐭𝐨 𝐔𝐬𝐞 📘💡", "𝐑𝐞𝐪𝐮𝐞𝐬𝐭 𝐚 𝐂𝐨𝐧𝐭𝐞𝐧𝐭 📝💌"]
]
reply_markup = ReplyKeyboardMarkup(menu_keyboard, resize_keyboard=True)

# ✅ Force Join Checker
async def check_force_join(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    user_id = update.effective_user.id
    not_joined = []

    for ch in FORCE_JOIN_CHANNELS:
        try:
            member = await context.bot.get_chat_member(ch, user_id)
            if member.status not in [ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
                not_joined.append(ch)
        except Exception as e:
            logging.warning(f"Join check failed for {ch}: {e}")
            not_joined.append(ch)

    if not_joined:
        text = (
            "🔒 <b>Access Locked!</b>\n"
            "📢 Please join the required channels first:\n\n" +
            "\n".join([f"➤ {c}" for c in not_joined]) +
            "\n\n✅ Then click “I've Joined” to unlock full features."
        )
        buttons = [[InlineKeyboardButton(c, url=f"https://t.me/{c.strip('@')}")] for c in not_joined]
        buttons.append([InlineKeyboardButton("✅ I've Joined", callback_data="check_joined")])

        try:
            if update.message:
                await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(buttons), parse_mode="HTML")
            elif update.callback_query:
                await update.callback_query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(buttons), parse_mode="HTML")
        except Exception as e:
            logging.error(f"Force join error: {e}")
            handle_bot_block(user_id)

        return False
    return True

# ✅ /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if is_banned(user_id):
        return

    if not await check_force_join(update, context):
        return

    if not is_user_allowed(update):
        return

    log_user(user_id)

    await context.bot.send_message(
        chat_id=user_id,
        text=(
            "🎬 <b>Welcome to CinePulseBot!</b> 🍿\n"
            "📺 Movies | Series | Anime | K-Dramas\n"
            "📥 HD Download (480p | 720p | 2K/4K)\n\n"
            "❓ Movie not found?\n"
            "😌 Relax & request here — <a href='https://t.me/cinepulsefam'>@cinepulsefam</a> 💌\n\n"
            "🛠 Admin: @Maiivishalhoon"
        ),
        reply_markup=reply_markup,
        parse_mode="HTML"
    )

# ✅ I've Joined button
async def joined_check_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    not_joined = []
    for ch in FORCE_JOIN_CHANNELS:
        try:
            member = await context.bot.get_chat_member(ch, user_id)
            if member.status not in [ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
                not_joined.append(ch)
        except Exception:
            not_joined.append(ch)

    if not_joined:
        text = (
            "❌ <b>You're still not joined all required channels.</b>\n\n" +
            "\n".join([f"➤ {c}" for c in not_joined]) +
            "\n\n📌 Please join and click again."
        )
        buttons = [[InlineKeyboardButton(c, url=f"https://t.me/{c.strip('@')}")] for c in not_joined]
        buttons.append([InlineKeyboardButton("✅ I've Joined", callback_data="check_joined")])
        await query.edit_message_text(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(buttons))
    else:
        await query.edit_message_text("✅ <b>Access Granted!</b>", parse_mode="HTML")
        await start(update, context)

# ✅ Handle All Buttons and Text Inputs
async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if is_banned(user_id):
        return

    if not await check_force_join(update, context):
        return

    if not is_user_allowed(update):
        return

    log_user(user_id)
    text = update.message.text

    # Category Navigation
    if text == "𝐋𝐚𝐭𝐞𝐬𝐭 𝐑𝐞𝐥𝐞𝐚𝐬𝐞𝐬 ✨🎞️":
        context.user_data["latest_page"] = 1
        await latest.show_latest(update, context, 1)
    elif text == "𝐀𝐧𝐢𝐦𝐞 💀🔥":
        context.user_data["anime_page"] = 1
        await anime.show_anime(update, context, 1)
    elif text == "𝐖𝐞𝐛𝐬𝐞𝐫𝐢𝐞𝐬 🎭📺":
        context.user_data["series_page"] = 1
        await series.show_series(update, context, 1)
    elif text == "𝐊-𝐃𝐫𝐚𝐦𝐚𝐬 💕✨":
        context.user_data["kdrama_page"] = 1
        await kdrama.show_kdrama(update, context, 1)
    elif text == "𝐒𝐨𝐮𝐭𝐡 𝐌𝐨𝐯𝐢𝐞𝐬 💣🔥":
        context.user_data["south_page"] = 1
        await south.show_south(update, context, 1)
    elif text == "𝐇𝐨𝐥𝐥𝐲𝐰𝐨𝐨𝐝 🎬🌍":
        context.user_data["hollywood_page"] = 1
        await hollywood.show_hollywood(update, context, 1)
    elif text == "𝐁𝐨𝐥𝐥𝐲𝐰𝐨𝐨𝐝 🌟🎥":
        context.user_data["bollywood_page"] = 1
        await bollywood.show_bollywood(update, context, 1)
    elif text == "𝐌𝐚𝐫𝐯𝐞𝐥 + 𝐃𝐂 🦸‍♂️⚡":
        context.user_data["marvel_page"] = 1
        await marvel.show_marvel(update, context, 1)
    elif text == "𝟏𝟖+ 𝐂𝐨𝐧𝐭𝐞𝐧𝐭 🔞🔥":
        context.user_data["eighteen_page"] = 1
        await eighteenplus.show_eighteen(update, context, 1)
    elif text == "𝗠𝘂𝗹𝘁𝗶-𝗣𝗮𝗿𝘁 𝗠𝗼𝘃𝗶𝗲𝘀 🎬":
        context.user_data["multipart_page"] = 1
        await multipart.show_multiparts(update, context, 1)
    elif text == "𝐇𝐨𝐰 𝐭𝐨 𝐔𝐬𝐞 📘💡":
        await send_how_to_use(update, context)
    elif text == "𝐑𝐞𝐪𝐮𝐞𝐬𝐭 𝐚 𝐂𝐨𝐧𝐭𝐞𝐧𝐭 📝💌":
        await handle_request(update, context)
    elif text == "𝐒𝐞𝐚𝐫𝐜𝐡 🔍🧠":
        await update.message.reply_text("🔍 Please type the name of the movie or series to search.")
    elif text == "🏠 Main Menu":
        context.user_data.clear()
        await update.message.reply_text("🏠 Back to main menu", reply_markup=reply_markup)
    else:
        # Pagination fallback OR direct search
        if context.user_data.get("anime_page"):
            await anime.handle_anime_buttons(update, context)
        elif context.user_data.get("series_page"):
            await series.handle_series_buttons(update, context)
        elif context.user_data.get("latest_page"):
            await latest.handle_latest_buttons(update, context)
        elif context.user_data.get("kdrama_page"):
            await kdrama.handle_kdrama_buttons(update, context)
        elif context.user_data.get("south_page"):
            await south.handle_south_buttons(update, context)
        elif context.user_data.get("hollywood_page"):
            await hollywood.handle_hollywood_buttons(update, context)
        elif context.user_data.get("bollywood_page"):
            await bollywood.handle_bollywood_buttons(update, context)
        elif context.user_data.get("marvel_page"):
            await marvel.handle_marvel_buttons(update, context)
        elif context.user_data.get("eighteen_page"):
            await eighteenplus.handle_eighteen_buttons(update, context)
        elif context.user_data.get("multipart_page"):
            await multipart.handle_multipart_buttons(update, context)
        else:
            await handle_search(update, context)

# ✅ Search Handler
async def handle_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if is_banned(user_id):
        return
    try:
        query = update.message.text.strip()
        result = search_movie(query)
        if result:
            title, poster, caption = result
            if poster:
                await update.message.reply_photo(photo=poster, caption=caption, parse_mode="HTML")
            else:
                await update.message.reply_text(caption, parse_mode="HTML")
        else:
            await update.message.reply_text("😔 No results found.")
    except Exception as e:
        logging.error(f"Search error: {e}")
        handle_bot_block(user_id)

# ✅ Run Bot
if __name__ == "__main__":
    print("🚀 Bot is starting...")
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(joined_check_callback, pattern="check_joined"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_buttons))
    print("✅ CinePulseBot is running...")
    app.run_polling()