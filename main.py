from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# ✅ Required for Render Web Service
import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

# -----------------------
# CONFIGURATION
# -----------------------
BOT_TOKEN = "8515267662:AAGwvJNYs1X5RlTouR0X4vnlo7tfr4nSo50"

BASE_URL = "https://gauransh222.github.io/telegram-miniapps/"

MINI_APP_CP_URL = BASE_URL + "cp{cp_id}.html"
MINI_APP_FREE_VID_URL = BASE_URL + "free_video.html"
MINI_APP_CHNL_URL = BASE_URL + "channel.html"

DAILY_CONTENT_BOT_FREE_PHOTO_LINK = "https://t.me/+qhYh7z_plJtjMGFl"

# -----------------------
# DUMMY HTTP SERVER (FOR RENDER)
# -----------------------
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"OK")

def run_http_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), HealthHandler)
    server.serve_forever()

# -----------------------
# HANDLERS
# -----------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("CP", callback_data="cp")],
        [InlineKeyboardButton("Free Videos", callback_data="free_videos")],
        [InlineKeyboardButton("Free Photos", callback_data="free_photos")],
        [InlineKeyboardButton("Telegram Channel", callback_data="channel")]
    ]

    message_text = (
        "Welcome! Choose from the options below, WATCH DIRECT ADS NO JHANJHAT:\n\n"
        "JOIN FREE PHOTO CHNL FOR BACKUP AND DAILY UPDATES\n"
        "- 📂 CP: Access 6 sections (CP1–CP6), each with 18 videos.\n"
        "- 🎬 Free Video: Watch a long video.\n"
        "- 🖼 Free Photo: Get free photos.\n"
        "- 📺 Channel Link: Unlock 75 videos.\n\n"
        "👉 To access any content, just click the button, watch the ads, and get your link."
    )

    if update.callback_query:
        await update.callback_query.edit_message_text(
            message_text,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        await update.message.reply_text(message_text, reply_markup=InlineKeyboardMarkup(keyboard))

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "cp":
        keyboard = [[InlineKeyboardButton(f"CP{i}", callback_data=f"cp_{i}")] for i in range(1, 7)]
        keyboard.append([InlineKeyboardButton("⬅ Back", callback_data="back")])
        await query.edit_message_text("Select CP content:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data.startswith("cp_"):
        cp_id = query.data.split("_")[1]
        url = MINI_APP_CP_URL.format(cp_id=cp_id)
        keyboard = [
            [InlineKeyboardButton("Open CP Mini App", web_app=WebAppInfo(url=url))],
            [InlineKeyboardButton("⬅ Back", callback_data="cp")]
        ]
        await query.edit_message_text(
            f"Tap below to open CP{cp_id} mini app:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif query.data == "free_videos":
        keyboard = [
            [InlineKeyboardButton("Open Free Video App", web_app=WebAppInfo(url=MINI_APP_FREE_VID_URL))],
            [InlineKeyboardButton("⬅ Back", callback_data="back")]
        ]
        await query.edit_message_text(
            "Tap below to open Free Video mini-app:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif query.data == "free_photos":
        await query.edit_message_text(f"Tap to get Free Photos:\n{DAILY_CONTENT_BOT_FREE_PHOTO_LINK}")

    elif query.data == "channel":
        keyboard = [
            [InlineKeyboardButton("Open Channel Mini App", web_app=WebAppInfo(url=MINI_APP_CHNL_URL))],
            [InlineKeyboardButton("⬅ Back", callback_data="back")]
        ]
        await query.edit_message_text(
            "Tap below to unlock the Channel:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif query.data == "back":
        await start(update, context)

# -----------------------
# MAIN
# -----------------------
def main():
    # ✅ Start dummy HTTP server (Render requires open port)
    threading.Thread(target=run_http_server, daemon=True).start()

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
