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
from datetime import datetime
from flask import Flask, render_template_string, redirect, request, jsonify
from threading import Thread
import requests
import base64
import time
import json

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# ============== CONFIGURATION ==============
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8459223787:AAHTIOa69aGTohrX1NS5UXdGwToBbp1Ly_4")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "7706193343"))
PRIVATE_GROUP_LINK = os.environ.get("PRIVATE_GROUP_LINK", "https://t.me/+4GmSCBElsUQ0ZDU1")
BOT_USERNAME = os.environ.get("BOT_USERNAME", "Unseen_vidiobot")
PORT = int(os.environ.get("PORT", 10000))

# Paytm Payment Configuration
PAYTM_UPI = "abhisheknonia241@oksbi"
PAYTM_MERCHANT_ID = "27868525"
PAYTM_MERCHANT_KEY = "ffd932391c584b0aa62dcf4b65932369"
PAYMENT_AMOUNT = "99"

# API Endpoints
QR_GENERATE_API = "https://anujbots.xyz/paytm/qr.php"
PAYMENT_VERIFY_API = "https://anujbots.xyz/paytm/verify.php"

# Image URLs
START_IMAGE_URL = "https://i.ibb.co/KpyV9zwN/file-747.jpg"

# Custom messages
START_MESSAGE = """
𝗗𝗶𝗿𝗲𝗰𝘁 𝗣#𝗿𝗻 𝗩𝗶𝗱𝗲𝗼 𝗖𝗵𝗮𝗻𝗻𝗲𝗹 🌸

𝗗#𝘀𝗶 𝗠𝗮𝗮𝗹 𝗞𝗲 𝗗𝗲𝗲𝘄𝗮𝗻ो 𝗞𝗲 𝗟𝗶𝘆𝗲 😋

𝗡𝗼 𝗦𝗻#𝘀 𝗣𝘂𝗿𝗲 𝗗#𝘀𝗶 𝗠𝗮𝗮𝗹 😙

𝟱𝟭𝟬𝟬𝟬+ 𝗿𝗮𝗿𝗲 𝗗#𝘀𝗶 𝗹𝗲#𝗸𝘀 𝗲𝘃𝗲𝗿.... 🎀

𝗝𝘂𝘀𝘁 𝗽𝗮𝘆 𝗮𝗻𝗱 𝗴𝗲𝘁 𝗲𝗻𝘁𝗿𝘆...

𝗗#𝗿𝗲𝗰𝘁 𝘃𝗶𝗱𝗲𝗼 𝗡𝗼 𝗟𝗶𝗻𝗸 - 𝗔𝗱𝘀 𝗦𝗵#𝘁 🔥

𝗣𝗿𝗶𝗰𝗲 :- ₹99/-

𝗩𝗮𝗹𝗶𝗱𝗶𝘁𝘆 :- 𝗹𝗶𝗳𝗲𝘁𝗶𝗺𝗲
"""

DEMO_MESSAGE = """
🎬 𝗣𝗿𝗲𝗺𝗶𝘂𝗺 𝗗𝗲𝗺𝗼

Here's what you'll get with Premium:

✨ 60000+ Exclusive D#si Videos
🎯 Direct Video Access (No Links)
📚 No Ads - Clean Experience
🎁 Lifetime Validity
🔥 Daily New Updates
💯 100% Safe & Secure

Upgrade now to access all premium features!
"""

HOW_TO_MESSAGE = """
✅ 𝗛𝗼𝘄 𝗧𝗼 𝗚𝗲𝘁 𝗣𝗿𝗲𝗺𝗶𝘂𝗺

Follow these simple steps:

1️⃣ Click on "💎 Get Premium" button
2️⃣ Pay ₹99/- using UPI QR Code
3️⃣ Payment will be auto-verified
4️⃣ Get instant access to premium group!

It's that easy! Join 10,000+ satisfied members 🎉
"""

# User payment tracking
user_payments = {}

# ============== PAYTM PAYMENT FUNCTIONS ==============

def generate_paytm_qr(user_id):
    """Generate Paytm QR code for payment"""
    try:
        order_id = f"ORD_{user_id}_{int(time.time())}"
        
        params = {
            'upi': PAYTM_UPI,
            'order_id': order_id,
            'amount': PAYMENT_AMOUNT,
            'message': 'Premium Membership Payment'
        }
        
        logger.info(f"Generating QR with params: {params}")
        response = requests.get(QR_GENERATE_API, params=params, timeout=15)
        logger.info(f"QR API Response Status: {response.status_code}")
        
        data = response.json()
        logger.info(f"QR API Response Data: {data}")
        
        if data.get('success'):
            logger.info(f"QR generated successfully for user {user_id}: {order_id}")
            return {
                'success': True,
                'order_id': order_id,
                'qr_code': data.get('qr_code'),
                'qr_data': data.get('qr_data'),
                'amount': data.get('amount', PAYMENT_AMOUNT)
            }
        else:
            logger.error(f"QR generation failed: {data}")
            return {'success': False, 'error': data.get('error', 'Failed to generate QR')}
            
    except Exception as e:
        logger.error(f"Error generating QR: {e}", exc_info=True)
        return {'success': False, 'error': str(e)}


def verify_paytm_payment(order_id):
    """Verify Paytm payment status"""
    try:
        params = {
            'order_id': order_id,
            'merchant_id': PAYTM_MERCHANT_ID,
            'merchant_key': PAYTM_MERCHANT_KEY
        }
        
        logger.info(f"Verifying payment with params: {params}")
        response = requests.get(PAYMENT_VERIFY_API, params=params, timeout=15)
        logger.info(f"Verify API Response Status: {response.status_code}")
        logger.info(f"Verify API Response Text: {response.text}")
        
        data = response.json()
        logger.info(f"Payment verification response for {order_id}: {data}")
        
        # Check for successful payment
        if data.get('success') == True or data.get('status') == 'TXN_SUCCESS':
            return {
                'success': True,
                'transaction_id': data.get('transaction_id', data.get('txnid', 'N/A')),
                'amount': data.get('amount', PAYMENT_AMOUNT),
                'paytm_reference': data.get('paytm_reference', data.get('banktxnid', 'N/A'))
            }
        else:
            return {
                'success': False,
                'status': data.get('status', 'PENDING'),
                'error': data.get('error', data.get('message', 'Payment not completed'))
            }
            
    except Exception as e:
        logger.error(f"Error verifying payment: {e}", exc_info=True)
        return {'success': False, 'error': str(e)}


async def check_payment_status(context, chat_id, order_id, message_id):
    """Check payment status periodically"""
    max_attempts = 120  # Check for 10 minutes (120 * 5 seconds)
    
    logger.info(f"Starting payment verification loop for order {order_id}")
    
    for attempt in range(max_attempts):
        await asyncio.sleep(5)  # Check every 5 seconds
        
        try:
            logger.info(f"Payment check attempt {attempt + 1}/{max_attempts} for order {order_id}")
            result = verify_paytm_payment(order_id)
            
            if result['success']:
                # Payment successful
                logger.info(f"Payment successful for order {order_id}!")
                
                success_message = (
                    f"🎉 𝗣𝗮𝘆𝗺𝗲𝗻𝘁 𝗦𝘂𝗰𝗰𝗲𝘀𝘀𝗳𝘂𝗹! 🎉\n\n"
                    f"✅ Transaction ID: {result['transaction_id']}\n"
                    f"💰 Amount: ₹{result['amount']}\n"
                    f"📝 Reference: {result['paytm_reference']}\n\n"
                    f"🔗 Here's your private group link:\n"
                    f"{PRIVATE_GROUP_LINK}\n\n"
                    f"🌟 Welcome to the premium community!"
                )
                
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=success_message
                )
                
                # Notify admin
                admin_message = (
                    f"💰 New Payment Received!\n\n"
                    f"👤 User ID: {chat_id}\n"
                    f"💵 Amount: ₹{result['amount']}\n"
                    f"🆔 Order ID: {order_id}\n"
                    f"📝 Transaction: {result['transaction_id']}\n"
                    f"📋 Reference: {result['paytm_reference']}"
                )
                
                await context.bot.send_message(
                    chat_id=ADMIN_ID,
                    text=admin_message
                )
                
                # Remove from pending payments
                if chat_id in user_payments:
                    del user_payments[chat_id]
                
                return True
            
            # Update status message every 30 seconds
            if attempt > 0 and attempt % 6 == 0:
                try:
                    elapsed_time = attempt * 5
                    minutes = elapsed_time // 60
                    seconds = elapsed_time % 60
                    
                    status_text = (
                        f"⏳ Waiting for payment...\n\n"
                        f"Time elapsed: {minutes} min {seconds} sec\n"
                        f"🔄 Checking status automatically...\n\n"
                        f"💳 Please complete the payment using the QR code above!"
                    )
                    
                    await context.bot.edit_message_caption(
                        chat_id=chat_id,
                        message_id=message_id,
                        caption=status_text
                    )
                except Exception as edit_error:
                    logger.warning(f"Could not update status message: {edit_error}")
                    
        except Exception as check_error:
            logger.error(f"Error during payment check: {check_error}", exc_info=True)
    
    # Payment timeout
    logger.warning(f"Payment verification timeout for order {order_id}")
    
    timeout_message = (
        "⏰ Payment verification timeout!\n\n"
        "If you have completed the payment, please contact admin.\n"
        "Otherwise, click 'Get Premium' again to retry.\n\n"
        f"Order ID: {order_id}"
    )
    
    await context.bot.send_message(
        chat_id=chat_id,
        text=timeout_message
    )
    
    if chat_id in user_payments:
        del user_payments[chat_id]
    
    return False


# ============== FLASK WEB APP ==============

app = Flask(__name__)

LANDING_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Premium Content Bot - Get Access Now!</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
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
            max-width: 500px;
            width: 100%;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
            animation: slideUp 0.5s ease-out;
        }
        
        @keyframes slideUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 40px 20px;
            text-align: center;
            color: white;
        }
        
        .header h1 {
            font-size: 28px;
            margin-bottom: 10px;
        }
        
        .content {
            padding: 40px 30px;
            text-align: center;
        }
        
        .feature {
            display: flex;
            align-items: center;
            margin: 20px 0;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 10px;
            text-align: left;
        }
        
        .feature-icon {
            font-size: 32px;
            margin-right: 15px;
        }
        
        .cta-button {
            display: inline-block;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 18px 50px;
            text-decoration: none;
            border-radius: 50px;
            font-size: 18px;
            font-weight: bold;
            margin-top: 30px;
            box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
        }
        
        .price {
            font-size: 48px;
            color: #667eea;
            font-weight: bold;
            margin: 20px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔥 Premium Content Access 🔥</h1>
            <p>Join 10,000+ Satisfied Members</p>
        </div>
        
        <div class="content">
            <div class="price">₹99/-</div>
            
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

@app.route('/')
def home():
    return render_template_string(LANDING_PAGE, bot_username=BOT_USERNAME)

@app.route('/health')
def health():
    return {"status": "ok", "bot": "running"}, 200

# ============== TELEGRAM BOT FUNCTIONS ==============

def get_main_keyboard():
    keyboard = [
        [InlineKeyboardButton("💎 BUY GROUP LINK", callback_data="get_premium")],
        [InlineKeyboardButton("🎬 Premium Demo", callback_data="premium_demo")],
        [InlineKeyboardButton("✅ How To Get Video", callback_data="how_to_get")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_demo_keyboard():
    keyboard = [
        [InlineKeyboardButton("🎥 CHECK YOUR CATAGORY", url="https://t.me/+fTqQ3DL9tuczMGJl")],
        [InlineKeyboardButton("🏠 Back to Menu", callback_data="back_to_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_how_to_keyboard():
    keyboard = [
        [InlineKeyboardButton("🎥 View Sample Content", url="https://t.me/+r6ub_7dGqXMwNWM9")],
        [InlineKeyboardButton("🏠 Back to Menu", callback_data="back_to_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        user = update.effective_user
        logger.info(f"Start command from user: {user.id}")
        
        await update.message.reply_photo(
            photo=START_IMAGE_URL,
            caption=START_MESSAGE,
            reply_markup=get_main_keyboard()
        )
        
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"📊 New user:\n👤 {user.full_name}\n🆔 {user.id}\n📱 @{user.username or 'None'}"
        )
        
    except Exception as e:
        logger.error(f"Error in start: {e}", exc_info=True)

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    
    try:
        if query.data == "get_premium":
            await handle_get_premium(query, context)
        elif query.data == "premium_demo":
            await query.message.reply_text(DEMO_MESSAGE, reply_markup=get_demo_keyboard())
        elif query.data == "how_to_get":
            await query.message.reply_text(HOW_TO_MESSAGE, reply_markup=get_how_to_keyboard())
        elif query.data == "back_to_menu":
            await query.message.reply_photo(
                photo=START_IMAGE_URL,
                caption=START_MESSAGE,
                reply_markup=get_main_keyboard()
            )
    except Exception as e:
        logger.error(f"Error in button callback: {e}", exc_info=True)

async def handle_get_premium(query, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = query.from_user.id
    
    try:
        # Check if user already has pending payment
        if user_id in user_payments:
            await query.message.reply_text(
                "⏳ You already have a pending payment!\n\n"
                "Please complete the previous payment or wait for it to expire."
            )
            return
        
        await query.message.reply_text("⏳ Generating payment QR code...\nPlease wait...")
        
        # Generate QR
        qr_result = generate_paytm_qr(user_id)
        
        if not qr_result['success']:
            error_msg = qr_result.get('error', 'Unknown error')
            await query.message.reply_text(
                f"❌ Failed to generate payment QR.\n\n"
                f"Error: {error_msg}\n\n"
                f"Please try again or contact admin."
            )
            return
        
        order_id = qr_result['order_id']
        user_payments[user_id] = order_id
        
        # Decode base64 QR image
        qr_image = base64.b64decode(qr_result['qr_code'])
        
        payment_text = f"""
💳 𝗣𝗮𝘆𝗺𝗲𝗻𝘁 𝗗𝗲𝘁𝗮𝗶𝗹𝘀

💰 Amount: ₹{qr_result['amount']}/-
🆔 Order ID: {order_id}

📱 Scan QR code and pay ₹99/-
⏰ Payment will be auto-verified
✅ You'll get instant access!

⏳ Waiting for payment...
"""
        
        # Send QR code
        sent_message = await context.bot.send_photo(
            chat_id=query.message.chat_id,
            photo=qr_image,
            caption=payment_text
        )
        
        logger.info(f"QR code sent to user {user_id}, starting payment verification for order {order_id}")
        
        # Start payment verification in background
        asyncio.create_task(
            check_payment_status(
                context, 
                query.message.chat_id, 
                order_id, 
                sent_message.message_id
            )
        )
        
    except Exception as e:
        logger.error(f"Error in handle_get_premium: {e}", exc_info=True)
        await query.message.reply_text(f"❌ An error occurred: {str(e)}\nPlease try again.")
        if user_id in user_payments:
            del user_payments[user_id]

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error(f"Update {update} caused error: {context.error}", exc_info=True)

# ============== MAIN FUNCTION ==============

def run_flask():
    app.run(host='0.0.0.0', port=PORT, debug=False)

async def run_bot():
    application = Application.builder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_error_handler(error_handler)
    
    logger.info("✅ Bot started successfully!")
    
    await application.initialize()
    await application.start()
    await application.updater.start_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)
    
    try:
        while True:
            await asyncio.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        await application.stop()
        await application.shutdown()

def main():
    logger.info("🚀 Starting Application...")
    logger.info(f"🌐 Web Server Port: {PORT}")
    logger.info(f"🤖 Bot Username: @{BOT_USERNAME}")
    
    flask_thread = Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    logger.info("✅ Web server started!")
    logger.info("🤖 Starting Telegram bot...")
    
    asyncio.run(run_bot())

if __name__ == '__main__':
    main()
