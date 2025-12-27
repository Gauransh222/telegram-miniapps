from dotenv import load_dotenv
load_dotenv()

import os
import asyncio
from datetime import datetime, timezone
from pymongo import MongoClient
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram.error import Forbidden
from aiohttp import web

# -------------------------------
# ENV
# -------------------------------
BOT_TOKEN = os.getenv("BOT_TOKEN")
MONGO_URI = os.getenv("MONGO_URI")
PORT = int(os.getenv("PORT", 8080))
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

if not BOT_TOKEN or not MONGO_URI or not ADMIN_ID:
    raise RuntimeError("BOT_TOKEN, MONGO_URI, ADMIN_ID must be set in .env")

# -------------------------------
# CONFIG
# -------------------------------
BASE_MINIAPP_URL = "https://telegram-miniapps-liart.vercel.app/"
DELETE_AFTER = 45*60

# -------------------------------
# CONTENT CONFIG
# -------------------------------
CONTENT_CONFIG = {
    "indian1":      {"channel": -1001111111111, "messages": list(range(1,61)), "html": "indian1.html"},
    "indian2":      {"channel": -1002222222222, "messages": list(range(1,61)), "html": "indian2.html"},
    "premium1":     {"channel": -1003333333333, "messages": list(range(1,61)), "html": "premium1.html"},
    "childvideos1": {"channel": -1004444444444, "messages": list(range(1,61)), "html": "childvideos1.html"},
    "indian1.1":    {"channel": -1005555555555, "messages": list(range(1,61)), "html": "indian1.1.html"},
    "indian1.2":    {"channel": -1006666666666, "messages": list(range(1,61)), "html": "indian1.2.html"}
}
VALID_KEYS = set(CONTENT_CONFIG.keys())

# -------------------------------
# DATABASE
# -------------------------------
mongo = MongoClient(MONGO_URI)
db = mongo["content_bot"]
users_col = db["users"]
access_col = db["access_log"]

# -------------------------------
# HELPERS
# -------------------------------
def save_user(user):
    """Save any interacting user"""
    user_id = user.id
    users_col.update_one(
        {"user_id": user_id},
        {"$setOnInsert": {
            "user_id": user_id,
            "username": user.username or "",
            "first_name": user.first_name or "",
            "joined_at": datetime.now(timezone.utc),
            "blocked": False,
        }},
        upsert=True
    )

def mark_blocked(user_id: int):
    users_col.update_one({"user_id": user_id}, {"$set": {"blocked": True}})

def log_access(user_id: int, key: str):
    access_col.insert_one({
        "user_id": user_id,
        "content": key,
        "timestamp": datetime.now(timezone.utc)
    })

# -------------------------------
# AUTO DELETE
# -------------------------------
async def auto_delete(bot, messages):
    await asyncio.sleep(DELETE_AFTER)
    for chat_id, msg_id in messages:
        try:
            await bot.delete_message(chat_id, msg_id)
        except Exception:
            pass

# -------------------------------
# SEND VIDEOS
# -------------------------------
async def send_videos(user_id, bot, key):
    cfg = CONTENT_CONFIG[key]
    sent = []

    for msg_id in cfg["messages"]:
        try:
            m = await bot.copy_message(chat_id=user_id, from_chat_id=cfg["channel"], message_id=msg_id)
            sent.append((user_id, m.message_id))
            await asyncio.sleep(0.6)
        except Forbidden:
            mark_blocked(user_id)
            return
        except Exception as e:
            print("Send error:", e)

    asyncio.create_task(auto_delete(bot, sent))

# -------------------------------
# START HANDLER
# -------------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    save_user(update.effective_user)
    user_id = update.effective_user.id
    args = context.args

    if not args:
        await update.message.reply_text(
            "✨ <b>Welcome to Premium Content Bot</b> ✨\n\n"
            "🎥 Exclusive private videos\n"
            "🔐 Access via special links only\n"
            "⏳ Content auto-deletes after 45 minutes",
            parse_mode="HTML"
        )
        return

    param = args[0]

    # Final unlock
    if param.endswith("_done"):
        key = param.replace("_done", "")
        if key not in VALID_KEYS:
            await update.message.reply_text("❌ Invalid or expired link.")
            return
        log_access(user_id, key)
        await update.message.reply_text("✅ <b>Access Confirmed</b>\n📤 Sending content…", parse_mode="HTML")
        await send_videos(user_id, context.bot, key)
        return

    # Initial access
    if param in VALID_KEYS:
        html_page = CONTENT_CONFIG[param]["html"]
        mini_app_url = BASE_MINIAPP_URL + html_page
        keyboard = [[InlineKeyboardButton("▶ Watch Ads to Unlock", web_app=WebAppInfo(mini_app_url))]]
        await update.message.reply_text(
            "🔒 <b>Locked Content</b>\nWatch 3 ads to unlock.",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="HTML"
        )
        return

    await update.message.reply_text("❌ Invalid access link.")

# -------------------------------
# ADMIN BROADCAST
# -------------------------------
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    if not context.args:
        await update.message.reply_text("Usage: /broadcast <your message here>")
        return
    text = " ".join(context.args)
    users = users_col.find({"blocked": False})
    count = 0
    for user in users:
        try:
            await context.bot.send_message(user["user_id"], text)
            count += 1
        except Forbidden:
            mark_blocked(user["user_id"])
        await asyncio.sleep(0.3)
    await update.message.reply_text(f"✅ Broadcast sent to {count} users.")

# -------------------------------
# ADMIN PANEL ENDPOINTS
# -------------------------------
async def admin_users(request):
    headers = request.headers
    user_id = int(headers.get("X-Admin-ID", 0))
    if user_id != ADMIN_ID:
        return web.Response(text="Unauthorized", status=401)
    
    users = []
    for u in users_col.find({}):
        last_access = access_col.find_one({"user_id": u["user_id"]}, sort=[("timestamp", -1)])
        users.append({
            "user_id": u["user_id"],
            "name": u.get("first_name") or "",
            "content": last_access["content"] if last_access else None,
            "joined_at": u["joined_at"].isoformat(),
            "blocked": u.get("blocked", False)
        })
    return web.json_response(users)

async def admin_broadcast(request):
    headers = request.headers
    user_id = int(headers.get("X-Admin-ID", 0))
    if user_id != ADMIN_ID:
        return web.Response(text="Unauthorized", status=401)
    
    data = await request.json()
    msg = data.get("message", "")
    count = 0
    for u in users_col.find({"blocked": False}):
        try:
            await app.bot.send_message(u["user_id"], msg)
            count += 1
        except Forbidden:
            mark_blocked(u["user_id"])
    return web.json_response({"status": f"Sent to {count} users"})

# -------------------------------
# HEALTHCHECK
# -------------------------------
async def healthcheck(request):
    return web.Response(text="OK")

# -------------------------------
# START WEB SERVER
# -------------------------------
async def start_web_server():
    web_app = web.Application()
    web_app.router.add_get("/", healthcheck)
    web_app.router.add_get("/admin/users", admin_users)
    web_app.router.add_post("/admin/broadcast", admin_broadcast)
    runner = web.AppRunner(web_app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()

# -------------------------------
# MAIN
# -------------------------------
async def main():
    global app
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("broadcast", broadcast))

    await start_web_server()
    print(f"Bot running on port {PORT}…")
    await app.initialize()
    await app.start()
    await app.bot.initialize()
    await app.updater.start_polling()
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
