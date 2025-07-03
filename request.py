# request.py

from telegram import Update
from telegram.ext import ContextTypes

async def handle_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 *𝐖𝐞𝐥𝐜𝐨𝐦𝐞 𝐅𝐫𝐢𝐞𝐧𝐝𝐬!*\n\n"
        "📢 *Want to request a movie or series?*\n"
        "🎯 *Drop your request here:*\n"
        "🖇️ [@cinepulsefam](https://t.me/cinepulsefam)\n\n"
        "📌 *𝐎𝐮𝐫 𝐭𝐞𝐚𝐦 𝐰𝐢𝐥𝐥 𝐮𝐩𝐥𝐨𝐚𝐝 𝐢𝐭 𝐀𝐒𝐀𝐏!*",
        parse_mode="Markdown"
    )
