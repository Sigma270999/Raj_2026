import logging
import os
import sys
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters
)
from telegram.error import TelegramError, NetworkError, TimedOut
import asyncio
from flask import Flask, render_template_string, jsonify
from threading import Thread
import time

# ============== LOGGING ==============
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# ============== CONFIGURATION ==============
BOT_TOKEN           = os.environ.get("BOT_TOKEN",          "8459223787:AAHTIOa69aGTohrX1NS5UXdGwToBbp1Ly_4")
ADMIN_ID            = int(os.environ.get("ADMIN_ID",        "8207112743"))
BOT_USERNAME        = os.environ.get("BOT_USERNAME",        "Unseen_vidiobot")
PORT                = int(os.environ.get("PORT",            10000))
PAYMENT_AMOUNT      = "59"

# ============== ASSETS ==============
START_IMAGE_URL = "https://i.ibb.co/KpyV9zwN/file-747.jpg"

# ✅ REPLACE THIS with your hosted QR image link (e.g. from imgbb, telegraph, etc.)
QR_IMAGE_URL = "https://freeimage.host/i/qUxX8JV"   # <-- PUT YOUR QR IMAGE LINK HERE

# ============== UPI INFO ==============
UPI_ID = "paytm.s1ooh26@pty"

# ============== MESSAGES ==============
START_MESSAGE = """
🔥 𝐏𝐑𝐄𝐌𝐈𝐔𝐌 𝐀𝐃𝐔𝐋𝐓 𝐂𝐎𝐋𝐋𝐄𝐂𝐓𝐈𝐎𝐍 𝐔𝐍𝐋𝐎𝐂𝐊𝐄𝐃 🔥

𝐇𝐃 + 𝐔𝐥𝐭𝐫𝐚-𝐅𝐫𝐞𝐬𝐡 𝐕𝐢𝐝𝐞𝐨𝐬 𝐀𝐯𝐚𝐢𝐥𝐚𝐛𝐥𝐞 𝐍𝐨𝐰

💦 𝐌𝐨𝐦-𝐒𝐨𝐧 𝐅𝐚𝐧𝐭𝐚𝐬𝐲
💦 𝐁𝐫𝐨𝐭𝐡𝐞𝐫-𝐒𝐢𝐬𝐭𝐞𝐫 𝐓𝐚𝐛𝐨𝐨
💦 𝐀𝐮𝐧𝐭𝐲 & 𝐁𝐡𝐚𝐛𝐡𝐢 𝐃𝐞𝐬𝐢 𝐇𝐨𝐭
💦 𝐓𝐞𝐞𝐧 𝐈𝐧𝐝𝐢𝐚𝐧 (𝟏𝟖+)
💦 𝐈𝐧𝐬𝐭𝐚𝐠𝐫𝐚𝐦 𝐑𝐞𝐞𝐥𝐬 𝐒𝐭𝐚𝐫𝐬
💦 𝐃𝐞𝐬𝐢 𝐁𝐡𝐚𝐛𝐡𝐢 & 𝐀𝐮𝐧𝐭𝐲 𝐒𝐞𝐫𝐢𝐞𝐬
💦 𝐅𝐨𝐫𝐞𝐢𝐠𝐧𝐞𝐫 & 𝐈𝐧𝐭𝐞𝐫𝐧𝐚𝐭𝐢𝐨𝐧𝐚𝐥
💦 𝐇𝐚𝐫𝐝𝐜𝐨𝐫𝐞 & 𝐑𝐨𝐥𝐞𝐩𝐥𝐚𝐲 𝐂𝐨𝐥𝐥𝐞𝐜𝐭𝐢𝐨𝐧

𝐀𝐥𝐥 𝐂𝐚𝐭𝐞𝐠𝐨𝐫𝐢𝐞𝐬 𝐢𝐧 𝐎𝐧𝐞 𝐏𝐚𝐜𝐤𝐚𝐠𝐞

💎 𝐎𝐧𝐥𝐲 𝐑𝐬 ₹59 𝐟𝐨𝐫 𝐋𝐢𝐦𝐢𝐭𝐞𝐝 𝐓𝐢𝐦𝐞 💎

✅ 𝐅𝐮𝐥𝐥 𝐇𝐃  𝐐𝐮𝐚𝐥𝐢𝐭𝐲
✅ 𝐈𝐧𝐬𝐭𝐚𝐧𝐭 𝐃𝐞𝐥𝐢𝐯𝐞𝐫𝐲
✅ 𝟏𝟎𝟎% 𝐖𝐨𝐫𝐤𝐢𝐧𝐠 & 𝐔𝐩𝐝𝐚𝐭𝐞𝐝 𝐋𝐢𝐧𝐤𝐬

𝐋𝐚𝐬𝐭 𝐟𝐞𝐰 𝐬𝐥𝐨𝐭𝐬 𝐚𝐭 ₹59→ 𝐃𝐨𝐧'𝐭 𝐦𝐢𝐬𝐬 𝐢𝐭!

👇 𝐂𝐥𝐢𝐜𝐤 💎 

BUY GROUP LINK 👇
CONTACT AND BUY PREMIUM

@VIDEOSELLER50R
@VIDEOSELLER50R
"""

HOW_TO_MESSAGE = """
📣HOW TO BUY MEMBERSHIP IN MY PAID GROUP✔️✔️

📣ALL PROCESS ISS VIDEO ME HAI 💞💞

BOT ~ @Unseen_vidiobot💞💞

OWNER ~ @VIDEOSELLER50R💞💞

📣  AGAR KOI ISSUE AATA HA TO AAP OWNER SE CONTACT KR  SKTE HA AAP💞💞
"""

DEMO_MESSAGE = """
👉 NOTE ~ YEH ONLY DEMO HAIN ASLI MAJA TO PREMIUM MEMBERSHIP LENE P MILGA USME 50K VIDEOS MILEGI HAR ROJ NEW VIDEOS AATI RHEGI 

👉BO AAPKI LIFETIME RHEGI👈

💎 BUY GROUP LINK
 PER CLICK KRO BOT M 
                   (👇👇👇👇)
BOT ~ @Unseen_vidiobot
"""

PAYMENT_CAPTION = """💎 *VIP ACCESS PAYMENT*
➖➖➖➖➖➖➖➖➖➖
🍑 ONE-TIME PAYMENT: ₹59 ONLY\\!
🔒 LIFETIME VALIDITY
➖➖➖➖➖➖➖➖➖➖

*HOW TO PAY:*
1️⃣ Scan the QR code with any UPI app
2️⃣ Pay exactly ₹59
3️⃣ Take a screenshot of the payment success
4️⃣ Send that screenshot HERE in this chat

✅ UPI ID: `paytm\\.s1ooh26@pty`

⏳ *Admin will verify & send you the group link within a few minutes\\!*"""

SCREENSHOT_RECEIVED_MESSAGE = """✅ *Screenshot Received\\!*

📸 Your payment screenshot has been sent to admin for verification\\.

⏳ *Admin will verify and send you the group link soon\\!*

If not received within 10 minutes, contact: @VIDEOSELLER50R"""

# ============== STATE: track users waiting for screenshot ==============
# { user_id: True }  — set when QR is shown, cleared when screenshot sent
awaiting_screenshot: set = set()


# ============================================================
#  TELEGRAM KEYBOARDS
# ============================================================

def get_main_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💎 BUY GROUP LINK",      callback_data="get_premium")],
        [InlineKeyboardButton("🎬 Premium Demo",         callback_data="premium_demo")],
        [InlineKeyboardButton("✅ How To Get Video",      callback_data="how_to_get")]
    ])

def get_demo_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🎥 CHECK YOUR CATAGORY", url="https://t.me/+uJdan9xFRttlMzQ1")],
        [InlineKeyboardButton("🏠 Back to Menu",         callback_data="back_to_menu")]
    ])

def get_how_to_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🎥 View Sample Content", url="https://t.me/+_aP0nl0V9LVkMjJl")],
        [InlineKeyboardButton("🏠 Back to Menu",         callback_data="back_to_menu")]
    ])

def get_cancel_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("❌ Cancel",               callback_data="cancel_payment")],
        [InlineKeyboardButton("🏠 Back to Menu",         callback_data="back_to_menu")]
    ])


# ============================================================
#  BOT HANDLERS
# ============================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    logger.info(f"[START] User {user.id} ({user.full_name})")
    try:
        await update.message.reply_photo(
            photo=START_IMAGE_URL,
            caption=START_MESSAGE,
            reply_markup=get_main_keyboard()
        )
        try:
            await context.bot.send_message(
                chat_id=ADMIN_ID,
                text=f"📊 *New User Started Bot*\n👤 {user.full_name}\n🆔 `{user.id}`\n📱 @{user.username or 'None'}",
                parse_mode="Markdown"
            )
        except Exception:
            pass
    except Exception as e:
        logger.error(f"[START] Error: {e}", exc_info=True)
        try:
            await update.message.reply_text("❌ Something went wrong. Please try /start again.")
        except Exception:
            pass


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    data = query.data

    try:
        if data == "get_premium":
            await handle_get_premium(query, context)

        elif data == "premium_demo":
            await query.message.reply_text(DEMO_MESSAGE, reply_markup=get_demo_keyboard())

        elif data == "how_to_get":
            await query.message.reply_text(HOW_TO_MESSAGE, reply_markup=get_how_to_keyboard())

        elif data == "cancel_payment":
            user_id = query.from_user.id
            awaiting_screenshot.discard(user_id)
            await query.message.reply_text(
                "❌ Payment cancelled. You can start again anytime.",
                reply_markup=get_main_keyboard()
            )

        elif data == "back_to_menu":
            try:
                await query.message.reply_photo(
                    photo=START_IMAGE_URL,
                    caption=START_MESSAGE,
                    reply_markup=get_main_keyboard()
                )
            except Exception:
                await query.message.reply_text(START_MESSAGE, reply_markup=get_main_keyboard())

    except Exception as e:
        logger.error(f"[CALLBACK] Error on '{data}': {e}", exc_info=True)
        try:
            await query.message.reply_text("❌ Something went wrong. Please try again.")
        except Exception:
            pass


async def handle_get_premium(query, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = query.from_user.id
    chat_id = query.message.chat_id

    # Mark user as awaiting screenshot
    awaiting_screenshot.add(user_id)

    try:
        await context.bot.send_photo(
            chat_id=chat_id,
            photo=QR_IMAGE_URL,
            caption=PAYMENT_CAPTION,
            parse_mode="MarkdownV2",
            reply_markup=get_cancel_keyboard()
        )
        logger.info(f"[PREMIUM] QR shown to user {user_id}")
    except Exception as e:
        logger.error(f"[PREMIUM] Failed to send QR: {e}")
        awaiting_screenshot.discard(user_id)
        await query.message.reply_text(
            "❌ Could not load QR code. Please try again or contact @VIDEOSELLER50R",
            reply_markup=get_main_keyboard()
        )


async def handle_screenshot(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Called when a user sends a photo.
    If they are in awaiting_screenshot, forward screenshot to admin.
    """
    user = update.effective_user
    user_id = user.id
    chat_id = update.effective_chat.id

    if user_id not in awaiting_screenshot:
        # Not expecting a screenshot from this user — ignore
        return

    logger.info(f"[SCREENSHOT] Received from user {user_id}")

    # Tell user we got it
    try:
        await update.message.reply_text(
            SCREENSHOT_RECEIVED_MESSAGE,
            parse_mode="MarkdownV2"
        )
    except Exception as e:
        logger.warning(f"[SCREENSHOT] Could not reply to user: {e}")
        await update.message.reply_text(
            "✅ Screenshot received! Admin will verify and send the group link soon."
        )

    # Forward screenshot to admin with user info
    try:
        photo_file_id = update.message.photo[-1].file_id  # highest quality
        admin_caption = (
            f"📸 *New Payment Screenshot*\n\n"
            f"👤 Name: {user.full_name}\n"
            f"🆔 User ID: `{user_id}`\n"
            f"📱 Username: @{user.username or 'None'}\n\n"
            f"✅ Verify payment & send group link manually."
        )
        await context.bot.send_photo(
            chat_id=ADMIN_ID,
            photo=photo_file_id,
            caption=admin_caption,
            parse_mode="Markdown"
        )
        logger.info(f"[SCREENSHOT] Forwarded to admin for user {user_id}")
    except Exception as e:
        logger.error(f"[SCREENSHOT] Could not forward to admin: {e}")

    # Remove from awaiting set (one screenshot per cycle)
    awaiting_screenshot.discard(user_id)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    err = context.error
    if isinstance(err, (NetworkError, TimedOut)):
        logger.warning(f"[ERROR] Network/Timeout: {err}")
    else:
        logger.error(f"[ERROR] Unhandled exception: {err}", exc_info=True)


# ============================================================
#  FLASK WEB APP
# ============================================================

flask_app = Flask(__name__)

LANDING_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Premium Content Bot</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex; align-items: center; justify-content: center; padding: 20px;
        }
        .container {
            max-width: 500px; width: 100%; background: white;
            border-radius: 20px; box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden; animation: slideUp 0.5s ease-out;
        }
        @keyframes slideUp {
            from { opacity: 0; transform: translateY(30px); }
            to   { opacity: 1; transform: translateY(0); }
        }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 40px 20px; text-align: center; color: white; }
        .header h1 { font-size: 28px; margin-bottom: 10px; }
        .content { padding: 40px 30px; text-align: center; }
        .feature { display: flex; align-items: center; margin: 20px 0; padding: 15px; background: #f8f9fa; border-radius: 10px; text-align: left; }
        .feature-icon { font-size: 32px; margin-right: 15px; }
        .cta-button {
            display: inline-block;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white; padding: 18px 50px;
            text-decoration: none; border-radius: 50px;
            font-size: 18px; font-weight: bold; margin-top: 30px;
            box-shadow: 0 10px 30px rgba(102,126,234,0.4);
        }
        .price { font-size: 48px; color: #667eea; font-weight: bold; margin: 20px 0; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔥 Premium Content Access 🔥</h1>
            <p>Join 10,000+ Satisfied Members</p>
        </div>
        <div class="content">
            <div class="price">₹59/-</div>
            <div class="feature"><div class="feature-icon">🎬</div><div>60,000+ Exclusive Videos</div></div>
            <div class="feature"><div class="feature-icon">🚀</div><div>Direct Access - No Ads</div></div>
            <div class="feature"><div class="feature-icon">💯</div><div>Lifetime Validity</div></div>
            <a href="https://t.me/{{ bot_username }}" class="cta-button">🚀 Get Access Now</a>
        </div>
    </div>
</body>
</html>
"""

@flask_app.route("/")
def home():
    return render_template_string(LANDING_PAGE, bot_username=BOT_USERNAME)

@flask_app.route("/health")
def health():
    return jsonify({"status": "ok", "bot": "running", "timestamp": int(time.time())}), 200


# ============================================================
#  STARTUP
# ============================================================

def run_flask():
    flask_app.run(host="0.0.0.0", port=PORT, debug=False, use_reloader=False)


async def run_bot():
    application = (
        Application.builder()
        .token(BOT_TOKEN)
        .connect_timeout(30)
        .read_timeout(30)
        .write_timeout(30)
        .build()
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_callback))
    # Handle photos (screenshots) from users
    application.add_handler(MessageHandler(filters.PHOTO, handle_screenshot))
    application.add_error_handler(error_handler)

    logger.info("✅ Bot handlers registered")

    await application.initialize()
    await application.start()
    await application.updater.start_polling(
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True
    )

    logger.info("🤖 Bot is polling...")

    try:
        while True:
            await asyncio.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        logger.info("🛑 Shutting down...")
    finally:
        await application.updater.stop()
        await application.stop()
        await application.shutdown()


def main():
    logger.info("🚀 Starting Application...")
    logger.info(f"🌐 Port: {PORT}")
    logger.info(f"🤖 Bot: @{BOT_USERNAME}")
    logger.info(f"💰 Price: ₹{PAYMENT_AMOUNT}")
    logger.info(f"📸 Mode: Manual screenshot verification")

    flask_thread = Thread(target=run_flask, daemon=True)
    flask_thread.start()
    logger.info("✅ Flask web server started")

    asyncio.run(run_bot())


if __name__ == "__main__":
    main()
