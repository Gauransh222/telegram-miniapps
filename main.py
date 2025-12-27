from dotenv import load_dotenv
load_dotenv()

import os
import asyncio
from datetime import datetime
from pymongo import MongoClient
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# -----------------------
# ENV VARIABLES
# -----------------------
BOT_TOKEN = os.getenv("BOT_TOKEN")
MONGO_URI = os.getenv("MONGO_URI")

# -----------------------
# DATABASE SETUP
# -----------------------
mongo_client = MongoClient(MONGO_URI)
mongo_db = mongo_client["content_bot"]
access_collection = mongo_db["access_log"]

def log_user_access(user_id: int, content: str):
    access_collection.insert_one({
        "user_id": user_id,
        "content": content,
        "timestamp": datetime.utcnow()
    })

# -----------------------
# CONSTANTS
# -----------------------
BASE_URL = "https://gauransh222.github.io/telegram-miniapps/"
MINI_APP_CP_URL = BASE_URL + "cp{cp_id}.html"
MINI_APP_FREE_VID_URL = BASE_URL + "free_video.html"
MINI_APP_CHNL_URL = BASE_URL + "channel.html"

# Storage channel for videos
STORAGE_CHANNEL_ID = -1001234567890  # 🔴 Replace with your channel ID

# Mapping of content to 60 video message IDs
CONTENT_MAP = {
    "cp11": list(range(1, 61)),
    "cp21": list(range(61, 121)),
    "premium1": list(range(121, 181)),
    "chnl1": list(range(181, 241))
}

DELETE_AFTER = 45 * 60  # 45 minutes auto-delete

# -----------------------
# VIDEO FUNCTIONS
# -----------------------
async def delete_messages_after_delay(user_id, bot, message_ids):
    await asyncio.sleep(DELETE_AFTER)
    for mid in message_ids:
        try:
            await bot.delete_message(chat_id=user_id, message_id=mid)
            await asyncio.sleep(0.2)
        except Exception as e:
            print(f"Failed to delete {mid}: {e}")

async def send_videos(user_id, bot, key):
    video_ids = CONTENT_MAP.get(key, [])
    sent_message_ids = []

    for msg_id in video_ids:
        try:
            sent = await bot.copy_message(
                chat_id=user_id,
                from_chat_id=STORAGE_CHANNEL_ID,
                message_id=msg_id
            )
            sent_message_ids.append(sent.message_id)
            await asyncio.sleep(0.6)  # anti-flood
        except Exception as e:
            print(f"Failed to send {msg_id}: {e}")

    # schedule deletion
    asyncio.create_task(delete_messages_after_delay(user_id, bot, sent_message_ids))

# -----------------------
# BOT HANDLERS
# -----------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    user_id = update.effective_user.id

    # ---------- HANDLE START PARAM ----------
    if args:
        key = args[0]

        # FINAL unlock param from mini-app
        if key.endswith("_done"):
            base_key = key.replace("_done", "")
            log_user_access(user_id, base_key)
            await update.message.reply_text(
                f"✅ Access confirmed for **{base_key.upper()}**!\n"
                "📤 Sending 60 videos now...\n"
                "⏳ Videos will auto-delete after 45 minutes.",
                parse_mode="Markdown"
            )
            await send_videos(user_id, context.bot, base_key)
            return

        # Initial param from channel
        else:
            mini_app_url = MINI_APP_CP_URL.format(cp_id=key)
            keyboard = [
                [InlineKeyboardButton(f"Watch {key} Mini-App", web_app=WebAppInfo(url=mini_app_url))]
            ]
            await update.message.reply_text(
                f"👆 Click below to open the mini-app for **{key.upper()}**.\n"
                "You need to complete the 3 ads inside to unlock the final button.",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            return

    # ---------- DEFAULT START MENU ----------
    keyboard = [
        [InlineKeyboardButton("CP11", callback_data="cp11")],
        [InlineKeyboardButton("CP21", callback_data="cp21")],
        [InlineKeyboardButton("Premium1", callback_data="premium1")],
        [InlineKeyboardButton("Channel1", callback_data="chnl1")]
    ]
    message_text = (
        "Welcome! Select content to unlock:\n\n"
        "- CP11 / CP21 / Premium1 / Channel1\n"
        "After completing mini-app ads, click the final unlock button to get videos."
    )

    if update.callback_query:
        await update.callback_query.edit_message_text(
            message_text,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        await update.message.reply_text(
            message_text,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    key = query.data

    mini_app_url = MINI_APP_CP_URL.format(cp_id=key)
    keyboard = [
        [InlineKeyboardButton(f"Watch {key} Mini-App", web_app=WebAppInfo(url=mini_app_url))],
        [InlineKeyboardButton("⬅ Back", callback_data="back")]
    ]
    await query.edit_message_text(
        f"Click below to open mini-app for **{key.upper()}**. Complete the 3 ads to unlock the final button.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    if key == "back":
        await start(update, context)

# -----------------------
# MAIN
# -----------------------
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("Bot is running with polling...")
    app.run_polling()

if __name__ == "__main__":
    main()
