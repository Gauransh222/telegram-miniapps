from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# -----------------------
# CONFIGURATION
# -----------------------
BOT_TOKEN = "8515267662:AAGwvJNYs1X5RlTouR0X4vnlo7tfr4nSo50"

BASE_URL = "https://gauransh222.github.io/telegram-miniapps/"

MINI_APP_CP_URL = BASE_URL + "cp{cp_id}.html"
MINI_APP_FREE_VID_URL = BASE_URL + "free_video.html"
MINI_APP_CHNL_URL = BASE_URL + "channel.html"

DAILY_CONTENT_BOT_FREE_PHOTO_LINK = "https://t.me/DailyyContentBot?start=free_photo"


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

    if update.callback_query:
        # Called when Back button is pressed → NO extra text here
        await update.callback_query.edit_message_text(
            "Welcome! Choose an option:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        # Called when user types /start → extra text here
        await update.message.reply_text("Bot has started successfully!")
        await update.message.reply_text(
            "Welcome! Choose an option:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # CP MENU
    if query.data == "cp":
        keyboard = [[InlineKeyboardButton(f"CP{i}", callback_data=f"cp_{i}")] for i in range(1, 7)]
        keyboard.append([InlineKeyboardButton("⬅ Back", callback_data="back")])
        await query.edit_message_text("Select CP content:", reply_markup=InlineKeyboardMarkup(keyboard))

    # OPEN CP MINI APP
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

    # FREE VIDEOS MINI APP
    elif query.data == "free_videos":
        keyboard = [
            [InlineKeyboardButton("Open Free Video App", web_app=WebAppInfo(url=MINI_APP_FREE_VID_URL))],
            [InlineKeyboardButton("⬅ Back", callback_data="back")]
        ]
        await query.edit_message_text(
            "Tap below to open Free Video mini-app:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    # FREE PHOTOS
    elif query.data == "free_photos":
        await query.edit_message_text(
            f"Tap to get Free Photos:\n{DAILY_CONTENT_BOT_FREE_PHOTO_LINK}"
        )

    # CHANNEL MINI APP
    elif query.data == "channel":
        keyboard = [
            [InlineKeyboardButton("Open Channel Mini App", web_app=WebAppInfo(url=MINI_APP_CHNL_URL))],
            [InlineKeyboardButton("⬅ Back", callback_data="back")]
        ]
        await query.edit_message_text(
            "Tap below to unlock the Channel:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    # BACK BUTTON
    elif query.data == "back":
        await start(update, context)


# -----------------------
# MAIN
# -----------------------
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("Main Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()