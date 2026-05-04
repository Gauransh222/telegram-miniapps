from dotenv import load_dotenv
load_dotenv()

import os
import asyncio
import threading
import json
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
MINI_APP_URL = os.getenv("MINI_APP_URL", "https://telegram-miniapps-liart.vercel.app")

# =======================
# REQUIRED JOIN CHANNELS
# =======================
JOIN_CHANNELS = [
    ("Channel 1", "https://t.me/+2KSxXSbNbZwyY2Rl", -1003636767769),
    ("Channel 2", "https://t.me/+VriQFTsENPg2ODdl", -1003326198393),
]

# =======================
# CONTENT CONFIG
# =======================
CONTENT_CONFIG = {
    "childvideos1": {
        "channel": -1003572102303,
        "page": "childvideos_page1.html",
        "ranges": {
            "set1": range(1, 10),
            "set2": range(11, 13),
            "set3": range(14, 15),
            "set4": range(16, 17),
            "set5": range(17, 19),
            "set6": range(19, 21),
            "set7": range(21, 22),
            "set8": range(22, 25),
            "set8": range(36, 38),
            "set9": range(38, 40),
            "set10": range(40, 42),
            "set11": range(42, 44),
            "set12": range(44, 46),
            "set13": range(46, 48),
            "set14": range(48, 50),
            "set15": range(50, 52),
            "set16": range(52, 54),
            "set17": range(54, 56),
            "set18": range(56, 58),
            "set19": range(58, 60),
            "set20": range(60, 62),
            "set21": range(62, 64),
            "set22": range(64, 66),
            "set23": range(66, 68),
            "set24": range(68, 70),
            "set25": range(70, 72),
            "set26": range(72, 74),
            "set27": range(74, 76),
            "set28": range(76, 78),
            "set29": range(78, 80),
            "set30": range(80, 82),
            "set31": range(82, 84),
            "set32": range(84, 86),
            "set33": range(86, 88),
            "set34": range(88, 90),
            "set35": range(90, 92),
            "set36": range(92, 94),
            "set37": range(94, 96),
            "set38": range(96, 98),
            "set39": range(98, 100),
            "set40": range(100, 102),
            "set41": range(102, 104),
            "set42": range(104, 106),
            "set43": range(106, 108),
            "set44": range(108, 110),
            "set45": range(110, 112),
            "set46": range(112, 114),
            "set47": range(114, 116),
            "set48": range(116, 118),
            "set49": range(118, 120),
            "set50": range(120, 122),
            "set51": range(122, 124),
            "set52": range(124, 126),
            "set53": range(126, 128),
            "set54": range(128, 130),
            "set55": range(130, 132),
            "set56": range(132, 134),
            "set57": range(134, 136),
        }
    },
    "indian1": {
        "channel": -1003571861534,
        "page": "indian_page1.html",
        "ranges": {
            "set1": range(1, 56),
            "set2": range(57, 96),
            "set3": range(97, 143),
            "set4": range(144, 166),
            "set5": range(166, 201),
            "set6": range(200, 243),
            "set7": range(243, 300),
            "set8": range(300,350),
            "set9": range(350, 382),
            "set10": range(382 , 402),
            "set11": range(403, 423),
            "set12": range(423, 443),
            "set13": range(443, 463),
            "set14": range(463, 483),
            "set15": range(483, 503),
            "set16": range(503, 523),
            "set17": range(523, 543),
            "set18": range(543, 563),
            "set19": range(563, 583),
            "set20": range(583, 603),
            "set21": range(603, 623),
            "set22": range(623, 643),
            "set23": range(643, 663),
            "set24": range(663, 683),
            "set25": range(683, 703),
            "set26": range(703, 723),
            "set27": range(723, 743),
            "set28": range(743, 763),
            "set29": range(763, 783),
            "set30": range(783, 803),
            "set31": range(803, 823),
            "set32": range(823, 843),
            "set33": range(843, 863),
            "set34": range(863, 883),
            "set35": range(883, 903),
            "set36": range(903, 923),
            "set37": range(923, 943),
            "set38": range(943, 963),
            "set39": range(963, 983),
            "set40": range(983, 1003),
            "set41": range(1003, 1023),
            "set42": range(1023, 1043),
            "set43": range(1043, 1063),
            "set44": range(1063, 1083),
            "set45": range(1083, 1103),
            "set46": range(1103, 1123),
            "set47": range(1123, 1143),
            "set48": range(1143, 1163),
            "set49": range(1163, 1183),
            "set50": range(1183, 1203),
            "set51": range(1203, 1223),
            "set52": range(1223, 1243),
            "set53": range(1243, 1263),
            "set54": range(1263, 1283),
            "set55": range(1283, 1303),
            "set56": range(1303, 1323),
            "set57": range(1323, 1343),
            "set58": range(1343, 1363),
            "set59": range(1363, 1383),
            "set60": range(1383, 1403),
            "set61": range(1403, 1423),
        }
    },
    "misc1": {
        "channel": -1003487224889,
        "page": "misc_page1.html",
        "ranges": {
            "set1": range(1, 9),
            "set2": range(10, 11),
            "set3": range(12, 13),
            "set4": range(14, 15),
            "set5": range(16, 17),
            "set6": range(18, 19),
            "set7": range(19, 21),
            "set8": range(21, 23),
            "set9": range(23, 25),
            "set10": range(25, 27),
            "set11": range(27, 29),
            "set12": range(29, 31),
            "set13": range(31, 33),
            "set14": range(33, 35),
            "set15": range(35, 37),
            "set16": range(37, 39),
            "set17": range(39, 41),
            "set18": range(41, 43),
            "set19": range(43, 45),
            "set20": range(45, 47),
            "set21": range(47, 49),
            "set22": range(49, 51),
            "set23": range(51, 53),
            "set24": range(53, 55),
            "set25": range(55, 57),
            "set26": range(57, 59),
            "set27": range(59, 61),
            "set28": range(61, 63),
            "set29": range(63, 65),
            "set30": range(65, 67),
            "set31": range(67, 69),
            "set32": range(69, 71),
            "set33": range(71, 73),
        }
    },
}

# =======================
# DATABASE
# =======================
mongo = MongoClient(MONGO_URI)
db = mongo["content_bot"]
users = db["users"]
access = db["access"]

users.create_index("user_id", unique=True)
users.create_index("last_seen")
access.create_index("time")
access.create_index("content")

bot_app = None
_event_loop = None  # ✅ store event loop for HTTP thread use


# =======================
# PARAM NORMALIZER
# ✅ FIX: "childvideos1" → "childvideos1_set1"
# ✅ "childvideos1_set3" stays as is
# =======================
def normalize_param(param: str) -> str:
    if not param:
        return ""
    param = param.strip()
    # Already has _set → keep as is
    if "_set" in param:
        return param
    # Has underscore but not _set (e.g. "childvideos1_done") → keep as is
    if "_" in param:
        return param
    # Just content type with no set → default to set1
    return param + "_set1"


# =======================
# HELPERS
# =======================
def save_user(user):
    """Called on every /start — stores every user in MongoDB."""
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


async def send_videos_to_user(user_id: int, raw: str):
    """
    Send videos from storage channel to user.
    raw = "childvideos1_set1" format
    """
    raw = raw.strip()

    # Strip _done if still present
    if raw.endswith("_done"):
        raw = raw[:-5]

    # Normalize — add _set1 if missing
    raw = normalize_param(raw)

    if "_" not in raw:
        return False

    # Split: "childvideos1_set1" → main="childvideos1", sub="set1"
    underscore_idx = raw.find("_")
    main = raw[:underscore_idx]
    sub = raw[underscore_idx + 1:]

    cfg = CONTENT_CONFIG.get(main)
    if not cfg or sub not in cfg["ranges"]:
        return False

    # Log unlock to MongoDB
    access.insert_one({
        "user_id": user_id,
        "content": f"{main}_{sub}",
        "time": datetime.now(timezone.utc)
    })

    try:
        await bot_app.bot.send_message(
            user_id,
            "✅ Access granted!\n📦 Sending your videos now…\n⚠️ Content auto-deletes in 45 minutes"
        )
    except:
        pass

    sent = []
    for msg_id in cfg["ranges"][sub]:
        try:
            m = await bot_app.bot.copy_message(
                chat_id=user_id,
                from_chat_id=cfg["channel"],
                message_id=msg_id
            )
            sent.append({"user_id": user_id, "msg_id": m.message_id})
            await asyncio.sleep(0.6)
        except Forbidden:
            return False
        except:
            pass

    asyncio.create_task(auto_delete(bot_app.bot, sent))
    return True


# =======================
# START COMMAND
# =======================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    save_user(user)  # ✅ always stores user in MongoDB

    if not context.args:
        await update.message.reply_text(
            "👋 Welcome!\nUse a valid access link from our channel to unlock free content."
        )
        return

    raw_param = context.args[0].strip()

    # ===== _done suffix = deliver videos =====
    if raw_param.endswith("_done"):
        raw = normalize_param(raw_param[:-5])
        result = await send_videos_to_user(user.id, raw)
        if not result:
            await update.message.reply_text("❌ Invalid or expired link.")
        return

    # ✅ FIX 3+4: normalize param before using
    param = normalize_param(raw_param)

    # ===== JOIN CHECK =====
    if not await check_joins(context.bot, user.id):
        buttons = [[InlineKeyboardButton(name, url=url)] for name, url, _ in JOIN_CHANNELS]
        buttons.append([InlineKeyboardButton("✅ I've Joined — Check Now", callback_data="check_join")])
        await update.message.reply_text(
            "🔒 Join our channels first to unlock free content:",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        context.user_data["pending"] = param
        return

    # ===== OPEN MINI APP =====
    # ✅ FIX 3: get content type from normalized param
    main = param.split("_")[0]
    cfg = CONTENT_CONFIG.get(main)

    if not cfg:
        await update.message.reply_text("❌ Invalid link.")
        return

    # ✅ FIX 3: correct URL — MINI_APP_URL + / + page filename + ?start=param
    mini_url = f"{MINI_APP_URL}/{cfg['page']}?start={param}&uid={user.id}"

    btn = [[InlineKeyboardButton("🎬 Watch & Unlock Free Content", web_app=WebAppInfo(mini_url))]]

    await update.message.reply_text(
        "🎬 *Your content is ready!*\n\nTap below to open the viewer. Takes less than 2 minutes.",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(btn)
    )


# =======================
# JOIN CALLBACK
# =======================
async def check_join_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    if not await check_joins(context.bot, q.from_user.id):
        await q.message.reply_text("❌ You haven't joined all channels yet. Please join and try again.")
        return

    param = context.user_data.get("pending")
    if not param:
        await q.message.reply_text("⚠️ Session expired. Please use the original link.")
        return

    main = param.split("_")[0]
    cfg = CONTENT_CONFIG.get(main)
    if not cfg:
        await q.message.reply_text("❌ Invalid link.")
        return

    mini_url = f"{MINI_APP_URL}/{cfg['page']}?start={param}&uid={q.from_user.id}"
    btn = [[InlineKeyboardButton("🎬 Watch & Unlock Free Content", web_app=WebAppInfo(mini_url))]]

    await q.message.reply_text(
        "✅ *Verified!* You're good to go.\n\nTap below to unlock your content:",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(btn)
    )


# =======================
# STATS (Admin only)
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

    per_content = list(access.aggregate([
        {"$group": {"_id": "$content", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]))

    lines = [f"• {c['_id']}: {c['count']}" for c in per_content]

    await update.message.reply_text(
        "📊 *BOT STATS*\n\n"
        "👥 *Users*\n"
        f"• Total: `{total_users}`\n"
        f"• Active 24h: `{active_24h}`\n"
        f"• Active 7d: `{active_7d}`\n\n"
        "🎬 *Unlocks*\n"
        f"• Total: `{total_unlocks}`\n"
        f"• Last 24h: `{unlocks_24h}`\n"
        f"• Last 7d: `{unlocks_7d}`\n\n"
        "📦 *By Content*\n" + ("\n".join(lines) if lines else "• None"),
        parse_mode="Markdown"
    )


# =======================
# BROADCAST (Admin only)
# =======================
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    if not context.args:
        await update.message.reply_text("Usage: /broadcast Your message here")
        return

    message = " ".join(context.args)
    sent = failed = 0
    for u in users.find({}):
        try:
            await context.bot.send_message(u["user_id"], message)
            sent += 1
            await asyncio.sleep(0.3)
        except:
            failed += 1
    await update.message.reply_text(f"✅ Sent: {sent}\n❌ Failed: {failed}")


# =======================
# HTTP SERVER
# /send-videos called by page3 after user clicks get videos
# =======================
class Handler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

    def do_HEAD(self):
        self.send_response(200)
        self.end_headers()

    def do_OPTIONS(self):
        """Handle CORS preflight from Vercel pages."""
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_POST(self):
        if self.path == "/send-videos":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length)
            try:
                data = json.loads(body)
                start_param = data.get("start_param", "").strip()
                user_id = data.get("user_id")

                if not user_id or not start_param:
                    self._respond(400, {"error": "missing user_id or start_param"})
                    return

                # Normalize
                raw = start_param[:-5] if start_param.endswith("_done") else start_param
                raw = normalize_param(raw)

                # ✅ FIX: use _event_loop stored at startup
                future = asyncio.run_coroutine_threadsafe(
                    send_videos_to_user(int(user_id), raw),
                    _event_loop
                )
                result = future.result(timeout=30)
                self._respond(200, {"ok": result})

            except Exception as e:
                self._respond(500, {"error": str(e)})
        else:
            self.send_response(404)
            self.end_headers()

    def _respond(self, status, body):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(body).encode())

    def log_message(self, format, *args):
        pass  # suppress logs


def run_http():
    port = int(os.environ.get("PORT", 10000))
    HTTPServer(("0.0.0.0", port), Handler).serve_forever()


# =======================
# MAIN
# ✅ FIX: use asyncio.run() to properly capture event loop
# =======================
async def main_async():
    global bot_app, _event_loop

    # ✅ Capture event loop BEFORE polling
    _event_loop = asyncio.get_event_loop()

    bot_app = Application.builder().token(BOT_TOKEN).build()
    bot_app.add_handler(CommandHandler("start", start))
    bot_app.add_handler(CommandHandler("stats", stats))
    bot_app.add_handler(CommandHandler("broadcast", broadcast))
    bot_app.add_handler(CallbackQueryHandler(check_join_cb, pattern="check_join"))

    # Start HTTP server in background thread
    threading.Thread(target=run_http, daemon=True).start()

    print("✅ Bot started...")

    await bot_app.initialize()
    await bot_app.start()
    await bot_app.updater.start_polling()

    # Run forever
    await asyncio.Event().wait()


def main():
    asyncio.run(main_async())


if __name__ == "__main__":
    main()