from telegram import Update
from telegram.ext import ContextTypes

async def send_how_to_use(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        "📘 *𝐂𝐢𝐧𝐞𝐏𝐮𝐥𝐬𝐞𝐁𝐨𝐭 कैसे यूज़ करें?*\n\n"
        "🎬 कोई भी category चुनो — Anime, Movies, K-Dramas etc.\n"
        "🔍 *Search* बटन दबाओ और जो चाहिए उसका नाम लिखो।\n\n"
        "🖼️ Poster दिखेगा और साथ में 🎯 download link मिलेगा।\n"
        "📥 Link पर tap करो → Ad skip करो → और मस्त watch/download करो!\n\n"
        "🚫 Bot को baar-baar block करोगे तो *permanently ban* हो जाओगे — no undo!\n\n"
        "✅ बस relax करो और enjoy करो — *one click, full entertainment!* ✨\n\n"
        "❓ *कोई भी दिक्कत हो या request डालनी हो?*\n"
        "💬 अपना issue यहाँ बताओ: [@cinepulsefam](https://t.me/cinepulsefam)"
    )

    if update.callback_query:
        await update.callback_query.edit_message_text(msg, parse_mode="Markdown", disable_web_page_preview=True)
    elif update.message:
        await update.message.reply_text(msg, parse_mode="Markdown", disable_web_page_preview=True)