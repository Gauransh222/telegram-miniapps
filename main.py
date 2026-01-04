from dotenv import load_dotenv
load_dotenv()

import os
import asyncio
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from datetime import datetime, timedelta, timezone
from pymongo import MongoClient

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    WebAppInfo,
)
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)
from telegram.error import Forbidden

# =======================
# ENV
# =======================
BOT_TOKEN = os.getenv("BOT_TOKEN")
MONGO_URI = os.getenv("MONGO_URI")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

# =======================
# REQUIRED JOIN CHANNELS
# =======================
JOIN_CHANNELS = [
    ("Channel 1", "https://t.me/+2KSxXSbNbZwyY2Rl", -1003636767769),
    ("Channel 2", "https://t.me/+VriQFTsENPg2ODdl", -1003326198393),
]

# =======================
# STORAGE CONFIG
# =======================
CONTENT_CONFIG = {
    "premium1": {
        "channel": -1003487224889,
        "html": "premium1.html",
        "ranges": {
            "set1": range(1, 9),
            "set2": range(10, 11),
            "set3": range(12, 13),
            "set4": range(14, 15),
        }
    },
    "indian1": {
        "channel": -1003571861534,
        "html": "indian1.html",
        "ranges": {
            "set1": range(1, 56),
            "set2": range(57, 96),
            "set3": range(97, 143),
            "set4": range(144, 175),
        }
    },
    "childvideos1": {
        "channel": -1003572102303,
        "html": "childvideos1.html",
        "ranges": {
            "set1": range(1, 10),
            "set2": range(11, 13),
            "set3": range(14,15),
            "set4": range(16, 17),
        }
    }
}

# =======================
# DATABASE
# =======================
mongo = MongoClient(MONGO_URI)
db = mongo["content_bot"]
users = db["users"]
access = db["access"]

# INDEXES (safe)
users.create_index("user_id", unique=True)
users.create_index("last_seen")
access.create_index("time")
access.create_index("content")

# =======================
# HELPERS
# =======================
def save_user(user):
    users.update_one(
        {"user_id": user.id},
        {"$set": {
            "user_id": user.id,
            "username": user.username,
            "first_name": user.first_name,
            "last_seen": datetime.now(timezone.utc)
        }},
        upsert=True
    )

async def check_joins(bot, user_id):
    for _, _, ch_id in JOIN_CHANNELS:
        try:
            member = await bot.get_chat_member(ch_id, user_id)
            if member.status not in ("member", "administrator", "creator"):
                return False
        except:
            return False
    return True

async def auto_delete(bot, records):
    await asyncio.sleep(45 * 60)
    for r in records:
        try:
            await bot.delete_message(r["user_id"], r["msg_id"])
        except:
            pass

# =======================
# START
# =======================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    save_user(user)

    if not context.args:
        await update.message.reply_text(
            "Welcome 👋\nUse a valid access link from this free 18+ channel"
        )
        return

    param = context.args[0]

    # ===== FINAL UNLOCK =====
    if param.endswith("_done"):
        raw = param[:-5]
        if "_" not in raw:
            await update.message.reply_text("Invalid link.")
            return

        main, sub = raw.split("_", 1)
        cfg = CONTENT_CONFIG.get(main)

        if not cfg or sub not in cfg["ranges"]:
            await update.message.reply_text("Invalid or expired link.")
            return

        access.insert_one({
            "user_id": user.id,
            "content": raw,
            "time": datetime.now(timezone.utc)
        })

        await update.message.reply_text(
            "✅ Access unlocked\n"
            "📦 Sending videos\n"
            "⚠️ Auto delete after 45 minutes"
        )

        sent = []
        for i, msg_id in enumerate(cfg["ranges"][sub], 1):
            try:
                m = await context.bot.copy_message(
                    chat_id=user.id,
                    from_chat_id=cfg["channel"],
                    message_id=msg_id
                )
                sent.append({"user_id": user.id, "msg_id": m.message_id})
                await asyncio.sleep(0.6)
            except Forbidden:
                return
            except:
                pass

        asyncio.create_task(auto_delete(context.bot, sent))
        return

    # ===== JOIN CHECK =====
    if not await check_joins(context.bot, user.id):
        buttons = [[InlineKeyboardButton(name, url=url)] for name, url, _ in JOIN_CHANNELS]
        buttons.append([InlineKeyboardButton("✅ I Joined", callback_data="check_join")])

        await update.message.reply_text(
            "🔒 Join required channels first",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        context.user_data["pending"] = param
        return

    # ===== MINI APP =====
    main = param.split("_")[0]
    cfg = CONTENT_CONFIG.get(main)

    if not cfg:
        await update.message.reply_text("Invalid link.")
        return

    mini_url = f"https://telegram-miniapps-liart.vercel.app/{cfg['html']}?start={param}"
    btn = [[InlineKeyboardButton("▶ Watch Ads", web_app=WebAppInfo(mini_url))]]

    await update.message.reply_text(
        "🔓 Almost done!\nWatch ads to unlock.",
        reply_markup=InlineKeyboardMarkup(btn)
    )

# =======================
# JOIN CALLBACK
# =======================
async def check_join_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    if not await check_joins(context.bot, q.from_user.id):
        await q.message.reply_text("❌ You haven’t joined all channels.")
        return

    param = context.user_data.get("pending")
    main = param.split("_")[0]
    cfg = CONTENT_CONFIG.get(main)

    mini_url = f"https://telegram-miniapps-liart.vercel.app/{cfg['html']}?start={param}"
    btn = [[InlineKeyboardButton("▶ Watch Ads", web_app=WebAppInfo(mini_url))]]

    await q.message.reply_text(
        "✅ Verified!\nNow watch ads to unlock.",
        reply_markup=InlineKeyboardMarkup(btn)
    )

# =======================
# STATS (NO TOP USERS)
# =======================
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    now = datetime.now(timezone.utc)
    day = now - timedelta(hours=24)
    week = now - timedelta(days=7)

    total_users = users.count_documents({})
    active_24h = users.count_documents({"last_seen": {"$gte": day}})
    active_7d = users.count_documents({"last_seen": {"$gte": week}})

    total_unlocks = access.count_documents({})
    unlocks_24h = access.count_documents({"time": {"$gte": day}})
    unlocks_7d = access.count_documents({"time": {"$gte": week}})

    per_content = access.aggregate([
        {"$group": {"_id": "$content", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ])

    content_lines = []
    for c in per_content:
        main = c["_id"].split("_")[0]
        content_lines.append(f"• {main}: {c['count']}")

    await update.message.reply_text(
        "📊 **BOT STATS**\n\n"
        "👥 Users\n"
        f"• Total: `{total_users}`\n"
        f"• Active 24h: `{active_24h}`\n"
        f"• Active 7d: `{active_7d}`\n\n"
        "🎬 Unlocks\n"
        f"• Total: `{total_unlocks}`\n"
        f"• Last 24h: `{unlocks_24h}`\n"
        f"• Last 7d: `{unlocks_7d}`\n\n"
        "📦 Unlocks by Content\n"
        + ("\n".join(content_lines) if content_lines else "• None"),
        parse_mode="Markdown"
    )

# =======================
# BROADCAST
# =======================
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    sent = 0
    for u in users.find({}):
        try:
            await context.bot.send_message(u["user_id"], update.message.text)
            sent += 1
            await asyncio.sleep(0.3)
        except:
            pass

    await update.message.reply_text(f"✅ Sent to {sent} users")

# =======================
# HTTP SERVER
# =======================
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is alive")

    def do_HEAD(self):
        self.send_response(200)
        self.end_headers()

def run_http_server():
    port = int(os.environ.get("PORT", 10000))
    HTTPServer(("0.0.0.0", port), HealthHandler).serve_forever()

# =======================
# MAIN
# =======================
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(CallbackQueryHandler(check_join_cb, pattern="check_join"))

    threading.Thread(target=run_http_server, daemon=True).start()
    app.run_polling()

if __name__ == "__main__":
    main()
