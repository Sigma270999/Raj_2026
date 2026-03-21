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
from telegram.error import TelegramError, NetworkError, TimedOut, BadRequest
import asyncio
from datetime import datetime
from flask import Flask, render_template_string, request, jsonify
from threading import Thread
import requests
import time
import json

# ============== LOGGING ==============
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# ============== CONFIGURATION ==============
BOT_TOKEN            = os.environ.get("BOT_TOKEN",          "8459223787:AAHTIOa69aGTohrX1NS5UXdGwToBbp1Ly_4")
ADMIN_ID             = int(os.environ.get("ADMIN_ID",        "8207112743"))
PRIVATE_GROUP_LINK   = os.environ.get("PRIVATE_GROUP_LINK", "https://t.me/+4GmSCBElsUQ0ZDU1")
BOT_USERNAME         = os.environ.get("BOT_USERNAME",        "Unseen_vidiobot")
PORT                 = int(os.environ.get("PORT",            10000))

# ============== PAYTM CONFIG ==============
PAYTM_UPI           = "paytm.s1ooh26@pty"
PAYTM_MERCHANT_ID   = "27868585"
PAYTM_MERCHANT_KEY  = "ffd932391c584b0aa62dcf4b65932369"
PAYMENT_AMOUNT      = "59"

# ============== API ENDPOINTS ==============
QR_API_URL      = "https://paytm.anujbots.xyz/qr.php"
VERIFY_API_URL  = "https://paytm.anujbots.xyz/verify.php"

# ============== ASSETS ==============
START_IMAGE_URL = "https://i.ibb.co/KpyV9zwN/file-747.jpg"

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

✅ 𝐅𝐮𝐥𝐥 𝐇𝐃  𝐐𝐮𝐚𝐥𝐢𝐭𝐲
✅ 𝐈𝐧𝐬𝐭𝐚𝐧𝐭 𝐃𝐞𝐥𝐢𝐯𝐞𝐫𝐲
✅ 𝟏𝟎𝟎% 𝐖𝐨𝐫𝐤𝐢𝐧𝐠 & 𝐔𝐩𝐝𝐚𝐭𝐞𝐝 𝐋𝐢𝐧𝐤𝐬

𝐋𝐚𝐬𝐭 𝐟𝐞𝐰 𝐬𝐥𝐨𝐭𝐬 𝐚𝐭 ₹59→ 𝐃𝐨𝐧’𝐭 𝐦𝐢𝐬𝐬 𝐢𝐭!

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
# ============== IN-MEMORY PAYMENT STORE ==============
# { user_id: { 'order_id': str, 'created_at': float, 'attempts': int } }
user_payments: dict = {}

PAYMENT_EXPIRY_SECONDS = 3600  # 1 hour (matches API QR expiry)
MAX_VERIFY_ATTEMPTS    = 120   # 120 × 5s = 10 minutes polling


# ============================================================
#  PAYTM API FUNCTIONS
# ============================================================

def generate_qr(user_id: int) -> dict:
    """
    Call paytm.anujbots.xyz/qr.php and return structured result.
    Returns: { success, order_id, qr_url, amount, expiry } or { success:False, error }
    """
    try:
        params = {
            "upi":     PAYTM_UPI,
            "amount":  PAYMENT_AMOUNT,
            "name":    "Premium Bot",
            "purpose": "Premium Membership"
        }
        logger.info(f"[QR] Calling {QR_API_URL} for user {user_id}")
        resp = requests.get(QR_API_URL, params=params, timeout=15)
        resp.raise_for_status()

        data = resp.json()
        logger.info(f"[QR] Response: {data}")

        if data.get("success"):
            return {
                "success":  True,
                "order_id": data["order_id"],
                "qr_url":   data["qr_url"],
                "amount":   str(data.get("amount", PAYMENT_AMOUNT)),
                "expiry":   data.get("expiry", int(time.time()) + PAYMENT_EXPIRY_SECONDS)
            }
        return {"success": False, "error": data.get("error", "QR generation failed")}

    except requests.exceptions.Timeout:
        logger.error("[QR] Timeout while calling QR API")
        return {"success": False, "error": "QR API timeout — please try again"}
    except requests.exceptions.ConnectionError:
        logger.error("[QR] Connection error while calling QR API")
        return {"success": False, "error": "Could not reach payment server — check internet"}
    except ValueError:
        logger.error("[QR] Invalid JSON from QR API")
        return {"success": False, "error": "Payment server returned invalid response"}
    except Exception as e:
        logger.error(f"[QR] Unexpected error: {e}", exc_info=True)
        return {"success": False, "error": f"Unexpected error: {str(e)}"}


def verify_payment(order_id: str) -> dict:
    """
    Call paytm.anujbots.xyz/verify.php and return structured result.
    Returns: { success, status, transaction_id, amount, paytm_reference,
               bank_reference, timestamp } or { success:False, status, error }
    """
    try:
        params = {
            "orderid":     order_id,
            "merchantid":  PAYTM_MERCHANT_ID,
            "merchantkey": PAYTM_MERCHANT_KEY
        }
        logger.info(f"[VERIFY] Checking order {order_id}")
        resp = requests.get(VERIFY_API_URL, params=params, timeout=15)
        resp.raise_for_status()

        data = resp.json()
        logger.info(f"[VERIFY] Response: {data}")

        status = data.get("status", "PENDING")

        if data.get("success") is True or status == "TXN_SUCCESS":
            return {
                "success":         True,
                "status":          "TXN_SUCCESS",
                "transaction_id":  data.get("transaction_id", "N/A"),
                "amount":          str(data.get("amount", PAYMENT_AMOUNT)),
                "paytm_reference": data.get("paytm_reference", "N/A"),
                "bank_reference":  data.get("bank_reference", "N/A"),
                "timestamp":       data.get("timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            }
        return {
            "success": False,
            "status":  status,
            "error":   data.get("error") or data.get("paytm_message") or "Payment not completed yet"
        }

    except requests.exceptions.Timeout:
        logger.warning(f"[VERIFY] Timeout for order {order_id}")
        return {"success": False, "status": "PENDING", "error": "Verify API timeout"}
    except requests.exceptions.ConnectionError:
        logger.warning(f"[VERIFY] Connection error for order {order_id}")
        return {"success": False, "status": "PENDING", "error": "Connection error during verify"}
    except ValueError:
        logger.error(f"[VERIFY] Invalid JSON for order {order_id}")
        return {"success": False, "status": "PENDING", "error": "Invalid verify response"}
    except Exception as e:
        logger.error(f"[VERIFY] Unexpected error: {e}", exc_info=True)
        return {"success": False, "status": "PENDING", "error": str(e)}


# ============================================================
#  PAYMENT POLLING LOOP
# ============================================================

async def poll_payment(context: ContextTypes.DEFAULT_TYPE, chat_id: int,
                       order_id: str, qr_message_id: int) -> None:
    """
    Poll verify API every 5 seconds up to MAX_VERIFY_ATTEMPTS.
    Sends success / timeout message and cleans up state.
    """
    logger.info(f"[POLL] Started polling for order {order_id}, chat {chat_id}")

    for attempt in range(1, MAX_VERIFY_ATTEMPTS + 1):
        await asyncio.sleep(5)

        # Check if payment was already cleaned up (e.g. duplicate call)
        if chat_id not in user_payments:
            logger.info(f"[POLL] Order {order_id} already resolved — stopping poll")
            return

        result = verify_payment(order_id)

        # ── SUCCESS ──────────────────────────────────────────
        if result["success"]:
            logger.info(f"[POLL] Payment SUCCESS for order {order_id}")

            success_msg = (
                f"🎉 *Payment Successful!* 🎉\n\n"
                f"✅ Transaction ID: `{result['transaction_id']}`\n"
                f"💰 Amount Paid: ₹{result['amount']}\n"
                f"📝 Paytm Ref: `{result['paytm_reference']}`\n"
                f"🏦 Bank Ref: `{result['bank_reference']}`\n"
                f"🕐 Time: {result['timestamp']}\n\n"
                f"🔗 *Your Private Group Link:*\n{PRIVATE_GROUP_LINK}\n\n"
                f"🌟 Welcome to the premium community!"
            )

            try:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=success_msg,
                    parse_mode="Markdown"
                )
            except Exception as e:
                logger.error(f"[POLL] Could not send success msg: {e}")
                # Fallback without markdown
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=success_msg.replace("*", "").replace("`", "")
                )

            # Notify admin
            try:
                admin_msg = (
                    f"💰 *New Payment Received!*\n\n"
                    f"👤 User ID: `{chat_id}`\n"
                    f"💵 Amount: ₹{result['amount']}\n"
                    f"🆔 Order: `{order_id}`\n"
                    f"📝 TxnID: `{result['transaction_id']}`\n"
                    f"📋 Paytm Ref: `{result['paytm_reference']}`\n"
                    f"🏦 Bank Ref: `{result['bank_reference']}`\n"
                    f"🕐 Time: {result['timestamp']}"
                )
                await context.bot.send_message(
                    chat_id=ADMIN_ID,
                    text=admin_msg,
                    parse_mode="Markdown"
                )
            except Exception as e:
                logger.error(f"[POLL] Could not notify admin: {e}")

            # Clean up
            user_payments.pop(chat_id, None)
            return

        # ── HARD FAILURE ─────────────────────────────────────
        if result.get("status") == "TXN_FAILURE":
            logger.warning(f"[POLL] TXN_FAILURE for order {order_id}")
            try:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=(
                        "❌ *Payment Failed!*\n\n"
                        "Your payment was declined by the bank.\n"
                        "Please try again with a different UPI method.\n\n"
                        "Click *💎 BUY GROUP LINK* to generate a new QR code."
                    ),
                    parse_mode="Markdown"
                )
            except Exception as e:
                logger.error(f"[POLL] Could not send failure msg: {e}")
            user_payments.pop(chat_id, None)
            return

        # ── STATUS UPDATE every 30 seconds (every 6th attempt) ──
        if attempt % 6 == 0:
            elapsed = attempt * 5
            mins, secs = divmod(elapsed, 60)
            try:
                await context.bot.edit_message_caption(
    chat_id=chat_id,
    message_id=qr_message_id,
    caption=(
        f"💎 *VIP ACCESS PAYMENT*\n"
        f"➖➖➖➖➖➖➖➖➖➖\n"
        f"🍑 ONE-TIME PAYMENT: ₹59 ONLY!\n"
        f"🔒 LIFETIME VALIDITY\n"
        f"➖➖➖➖➖➖➖➖➖➖\n"
        f"1️⃣ Scan QR & Pay ₹59\n"
        f"2️⃣ After pay send payment screenshot to\n"
        f"✅ UPI ID: paytm.s1ooh26@pty\n\n"
        f"⏳ Waiting... {mins}m {secs}s elapsed\n"
        f"🔄 Status: {result.get('status', 'PENDING')}"
    ),
    parse_mode="Markdown"
)
            except BadRequest:
                pass  # Message not modified or deleted — ignore
            except Exception as e:
                logger.warning(f"[POLL] Caption update failed: {e}")

    # ── TIMEOUT ──────────────────────────────────────────────
    logger.warning(f"[POLL] Timeout for order {order_id}")
    try:
        await context.bot.send_message(
            chat_id=chat_id,
            text=(
                f"⏰ *Payment Verification Timeout!*\n\n"
                f"QR code has expired (valid for 1 hour only).\n\n"
                f"• If you paid successfully, contact admin with Order ID:\n"
                f"`{order_id}`\n\n"
                f"• Otherwise, click *💎 BUY GROUP LINK* to try again."
            ),
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"[POLL] Could not send timeout msg: {e}")

    user_payments.pop(chat_id, None)


# ============================================================
#  FLASK WEB APP
# ============================================================

app = Flask(__name__)

LANDING_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Premium Content Bot - Get Access Now!</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        .container {
            max-width: 500px; width: 100%;
            background: white; border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
            animation: slideUp 0.5s ease-out;
        }
        @keyframes slideUp {
            from { opacity: 0; transform: translateY(30px); }
            to   { opacity: 1; transform: translateY(0); }
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 40px 20px; text-align: center; color: white;
        }
        .header h1 { font-size: 28px; margin-bottom: 10px; }
        .content { padding: 40px 30px; text-align: center; }
        .feature {
            display: flex; align-items: center;
            margin: 20px 0; padding: 15px;
            background: #f8f9fa; border-radius: 10px; text-align: left;
        }
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
            <div class="feature">
                <div class="feature-icon">🎬</div>
                <div>60,000+ Exclusive Videos</div>
            </div>
            <div class="feature">
                <div class="feature-icon">🚀</div>
                <div>Direct Access - No Ads</div>
            </div>
            <div class="feature">
                <div class="feature-icon">💯</div>
                <div>Lifetime Validity</div>
            </div>
            <a href="https://t.me/{{ bot_username }}" class="cta-button">
                🚀 Get Access Now
            </a>
        </div>
    </div>
</body>
</html>
"""

@app.route("/")
def home():
    from flask import render_template_string
    return render_template_string(LANDING_PAGE, bot_username=BOT_USERNAME)

@app.route("/health")
def health():
    return jsonify({"status": "ok", "bot": "running", "timestamp": int(time.time())}), 200


# ============================================================
#  TELEGRAM KEYBOARDS
# ============================================================

def get_main_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💎 BUY GROUP LINK",       callback_data="get_premium")],
        [InlineKeyboardButton("🎬 Premium Demo",          callback_data="premium_demo")],
        [InlineKeyboardButton("✅ How To Get Video",       callback_data="how_to_get")]
    ])

def get_demo_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🎥 CHECK YOUR CATAGORY",  url="https://t.me/+uJdan9xFRttlMzQ1")],
        [InlineKeyboardButton("🏠 Back to Menu",          callback_data="back_to_menu")]
    ])

def get_how_to_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🎥 View Sample Content",  url="https://t.me/+_aP0nl0V9LVkMjJl")],
        [InlineKeyboardButton("🏠 Back to Menu",          callback_data="back_to_menu")]
    ])

def get_cancel_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("❌ Cancel Payment",        callback_data="cancel_payment")],
        [InlineKeyboardButton("🏠 Back to Menu",          callback_data="back_to_menu")]
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
            pass  # Don't crash if admin notify fails
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
            if user_id in user_payments:
                order_id = user_payments[user_id].get("order_id", "N/A")
                user_payments.pop(user_id, None)
                await query.message.reply_text(
                    f"❌ Payment cancelled.\nOrder ID: `{order_id}`\n\nYou can start a new payment anytime.",
                    parse_mode="Markdown",
                    reply_markup=get_main_keyboard()
                )
            else:
                await query.message.reply_text("No pending payment found.", reply_markup=get_main_keyboard())

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
    user_id  = query.from_user.id
    chat_id  = query.message.chat_id

    # ── Already has a pending payment? ──
    if user_id in user_payments:
        existing = user_payments[user_id]
        created  = existing.get("created_at", 0)
        # If older than expiry, auto-clean and allow new one
        if time.time() - created > PAYMENT_EXPIRY_SECONDS:
            user_payments.pop(user_id, None)
            logger.info(f"[PREMIUM] Expired pending payment cleaned for {user_id}")
        else:
            remaining = int((PAYMENT_EXPIRY_SECONDS - (time.time() - created)) / 60)
            await query.message.reply_text(
                f"⏳ *You already have a pending payment!*\n\n"
                f"🆔 Order: `{existing['order_id']}`\n"
                f"⏰ Expires in ~{remaining} minutes\n\n"
                f"Please complete or cancel the current payment first.",
                parse_mode="Markdown",
                reply_markup=get_cancel_keyboard()
            )
            return

    # ── Generating message ──
    generating_msg = await query.message.reply_text("⏳ Generating payment QR code...\nPlease wait a moment...")

    # ── Generate QR ──
    qr_result = generate_qr(user_id)

    # Delete generating message
    try:
        await generating_msg.delete()
    except Exception:
        pass

    if not qr_result["success"]:
        await query.message.reply_text(
            f"❌ *Failed to generate QR code*\n\n"
            f"Error: {qr_result.get('error', 'Unknown')}\n\n"
            f"Please try again in a few seconds.\n"
            f"If the issue persists, contact admin.",
            parse_mode="Markdown",
            reply_markup=get_main_keyboard()
        )
        return

    order_id = qr_result["order_id"]
    qr_url   = qr_result["qr_url"]
    amount   = qr_result["amount"]

    # Store payment info
    user_payments[user_id] = {
        "order_id":   order_id,
        "created_at": time.time(),
        "attempts":   0
    }

    caption = (
        f"💳 *Payment Details*\n\n"
        f"💰 Amount: ₹{amount}/-\n"
        f"🆔 Order ID: `{order_id}`\n\n"
        f"📱 Scan this QR code with any UPI app\n"
        f"⏰ QR valid for 1 hour\n"
        f"🔄 Auto-verifying every 5 seconds\n\n"
        f"⏳ Waiting for payment..."
    )

    try:
        sent_msg = await context.bot.send_photo(
            chat_id=chat_id,
            photo=qr_url,
            caption=caption,
            parse_mode="Markdown",
            reply_markup=get_cancel_keyboard()
        )
    except Exception as e:
        logger.error(f"[PREMIUM] Failed to send QR photo: {e}")
        user_payments.pop(user_id, None)
        await query.message.reply_text(
            "❌ Could not send QR code image. Please try again.",
            reply_markup=get_main_keyboard()
        )
        return

    logger.info(f"[PREMIUM] QR sent to user {user_id}, order {order_id}, starting poll")

    # Start background polling
    asyncio.create_task(
        poll_payment(context, chat_id, order_id, sent_msg.message_id)
    )


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    err = context.error
    if isinstance(err, (NetworkError, TimedOut)):
        logger.warning(f"[ERROR] Network/Timeout: {err}")
    else:
        logger.error(f"[ERROR] Unhandled exception: {err}", exc_info=True)


# ============================================================
#  STARTUP
# ============================================================

def run_flask():
    app.run(host="0.0.0.0", port=PORT, debug=False, use_reloader=False)


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
    logger.info(f"📡 QR API: {QR_API_URL}")
    logger.info(f"📡 Verify API: {VERIFY_API_URL}")

    flask_thread = Thread(target=run_flask, daemon=True)
    flask_thread.start()
    logger.info("✅ Flask web server started")

    asyncio.run(run_bot())


if __name__ == "__main__":
    main()