"""
🚀 MEDICUSLABS - TELEGRAM BOT
Skin Disease Detection AI
No WhatsApp, No Twilio, No Replit needed!
Just Telegram + Railway (FREE with GitHub Student Pack)
"""

import os
import logging
import requests
from io import BytesIO
import numpy as np
import cv2
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ── LOGGING ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ── CONFIG ────────────────────────────────────────────────────────────────────
BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')

# ── LOAD MODEL ────────────────────────────────────────────────────────────────
model = None

def load_model():
    global model
    try:
        from ultralytics import YOLO
        model_path = 'medicuslabs_best.pt'
        if os.path.exists(model_path):
            model = YOLO(model_path)
            logger.info("✅ Model loaded successfully!")
        else:
            logger.warning("⚠️  Model file not found: medicuslabs_best.pt")
    except Exception as e:
        logger.error(f"❌ Model load error: {e}")

# ── DISEASE INFO ──────────────────────────────────────────────────────────────
DISEASE_INFO = {
    'acne': {
        'name': '🔴 Acne',
        'desc': 'Inflammatory skin condition with pimples & spots',
        'tips': [
            '• Use gentle, non-comedogenic cleanser twice daily',
            '• Avoid touching or popping pimples',
            '• Apply benzoyl peroxide or salicylic acid gel',
            '• Consult dermatologist if severe',
        ],
        'urgent': False
    },
    'eczema': {
        'name': '🔴 Eczema',
        'desc': 'Chronic inflammation causing dry, itchy skin',
        'tips': [
            '• Moisturize with thick cream immediately after bathing',
            '• Avoid soap, use gentle cleansers',
            '• Identify & avoid triggers (dust, pollen, stress)',
            '• Use prescribed steroid cream for flare-ups',
        ],
        'urgent': False
    },
    'psoriasis': {
        'name': '🔴 Psoriasis',
        'desc': 'Autoimmune disease causing thick scaly patches',
        'tips': [
            '• Keep skin moisturized at all times',
            '• Use medicated shampoo for scalp psoriasis',
            '• Manage stress — it triggers flare-ups',
            '• See dermatologist for prescription treatment',
        ],
        'urgent': False
    },
    'ringworm': {
        'name': '⚠️ Ringworm (Tinea)',
        'desc': 'Fungal infection — circular ring-shaped rash (contagious!)',
        'tips': [
            '• Apply antifungal cream (clotrimazole) twice daily',
            '• Keep affected area clean and dry',
            '• Do NOT share towels, clothes or bedsheets',
            '• Avoid scratching — it spreads!',
        ],
        'urgent': False
    },
    'vitiligo': {
        'name': '⚪ Vitiligo',
        'desc': 'Loss of skin pigmentation (white patches)',
        'tips': [
            '• Apply SPF 50+ sunscreen on white patches daily',
            '• Consider cosmetic cover-up if needed',
            '• Consult dermatologist for repigmentation therapy',
            '• Maintain healthy diet — Vitamin B12 & D3 help',
        ],
        'urgent': False
    },
    'melanoma': {
        'name': '🚨 MELANOMA',
        'desc': '⚠️ Possible skin cancer detected!',
        'tips': [
            '🚨 SEEK IMMEDIATE MEDICAL ATTENTION',
            '• Visit a dermatologist or oncologist TODAY',
            '• Do NOT delay — early detection saves lives',
            '• Avoid sun exposure on affected area',
        ],
        'urgent': True
    },
    'normal_skin': {
        'name': '✅ Normal Skin',
        'desc': 'No skin condition detected — skin looks healthy!',
        'tips': [
            '• Continue daily skincare routine',
            '• Apply sunscreen SPF 30+ every morning',
            '• Stay hydrated (8 glasses of water/day)',
            '• Do monthly self skin checks',
        ],
        'urgent': False
    },
    'normal': {
        'name': '✅ Normal Skin',
        'desc': 'No skin condition detected — skin looks healthy!',
        'tips': [
            '• Continue daily skincare routine',
            '• Apply sunscreen SPF 30+ every morning',
            '• Stay hydrated (8 glasses of water/day)',
        ],
        'urgent': False
    }
}

# ── PREDICTION ────────────────────────────────────────────────────────────────
def predict_disease(image_bytes: bytes):
    """Run YOLOv8 prediction on image bytes"""
    if model is None:
        return None, 0

    try:
        img_array = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

        if img is None:
            return None, 0

        img = cv2.resize(img, (224, 224))

        results = model.predict(img, verbose=False)
        result = results[0]

        if hasattr(result, 'probs') and result.probs is not None:
            class_id = result.probs.top1
            confidence = float(result.probs.top1conf)
            class_names = result.names
            predicted_class = class_names[class_id].lower()
            return predicted_class, confidence

    except Exception as e:
        logger.error(f"Prediction error: {e}")

    return None, 0

# ── FORMAT RESPONSE ───────────────────────────────────────────────────────────
def format_result(disease: str, confidence: float) -> str:
    info = DISEASE_INFO.get(disease, DISEASE_INFO.get('normal_skin'))

    tips_text = '\n'.join(info['tips'])

    if info['urgent']:
        header = f"🚨🚨🚨 URGENT ALERT 🚨🚨🚨"
    else:
        header = "🔬 MedicusLabs AI Analysis"

    msg = f"""{header}

{info['name']}

📋 *Description:*
{info['desc']}

📊 *AI Confidence:* `{confidence:.1%}`

💊 *Recommendations:*
{tips_text}

━━━━━━━━━━━━━━━━━━━━
⚕️ *DISCLAIMER:* This is AI-assisted analysis only. Always consult a qualified dermatologist for proper diagnosis and treatment.

📱 Send another photo anytime!"""

    return msg

# ── HANDLERS ──────────────────────────────────────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome = """👋 *Welcome to MedicusLabs AI!*

🔬 I can detect *7 skin conditions* from photos:

• 🔴 Acne
• 🔴 Eczema
• 🔴 Psoriasis
• ⚠️ Ringworm
• ⚪ Vitiligo
• 🚨 Melanoma
• ✅ Normal Skin

━━━━━━━━━━━━━━━━━━━━
📸 *Just send me a photo of the skin area!*

I'll analyze it in seconds and give you:
✓ Disease identification
✓ Confidence score
✓ Medical recommendations

━━━━━━━━━━━━━━━━━━━━
⚕️ For educational purposes only. Always consult a doctor.

📸 *Send your photo now!*"""

    await update.message.reply_text(welcome, parse_mode='Markdown')


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """🆘 *MedicusLabs Help*

*How to use:*
1️⃣ Take a clear photo of affected skin area
2️⃣ Send the photo in this chat
3️⃣ Get instant AI analysis!

*Tips for best results:*
• Good lighting (natural light preferred)
• Close-up photo (5-15 cm distance)
• Keep camera steady
• Show the affected area clearly

*Commands:*
/start — Welcome message
/help — This help guide
/about — About MedicusLabs

*Detects 7 conditions:*
🔴 Acne, Eczema, Psoriasis
⚠️ Ringworm (contagious!)
⚪ Vitiligo
🚨 Melanoma (serious — see doctor!)
✅ Normal Skin

━━━━━━━━━━━━━━━━━━━━
⚕️ Always consult a dermatologist for proper diagnosis!"""

    await update.message.reply_text(help_text, parse_mode='Markdown')


async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    about = """ℹ️ *About MedicusLabs*

🤖 *AI Model:* YOLOv8 Medium
📊 *Training Data:* 500,000+ images (83.6 GB)
🎯 *Accuracy:* 85%+
🏥 *Classes:* 7 skin conditions
⚡ *Speed:* <3 seconds

👥 *Team:*
• Mallikarjun R — AI Lead
• Mohammad Adil — Backend
• Mallanagowda M — Deployment
• Nigam Patel — Testing

🎓 DSATM, Bengaluru

━━━━━━━━━━━━━━━━━━━━
⚕️ *Medical Disclaimer:*
This tool is for educational purposes only. It is NOT a replacement for professional medical diagnosis. Always consult a qualified dermatologist."""

    await update.message.reply_text(about, parse_mode='Markdown')


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming photos"""
    await update.message.reply_text("🔬 Analyzing your skin image... Please wait!")

    try:
        # Get highest quality photo
        photo = update.message.photo[-1]
        photo_file = await context.bot.get_file(photo.file_id)

        # Download image
        photo_bytes = await photo_file.download_as_bytearray()

        if model is None:
            await update.message.reply_text(
                "⚠️ AI model is loading. Please try again in 30 seconds!"
            )
            return

        # Predict
        disease, confidence = predict_disease(bytes(photo_bytes))

        if disease is None:
            await update.message.reply_text(
                "❌ Could not analyze the image.\n\nPlease:\n• Send a clearer photo\n• Make sure it shows skin clearly\n• Try better lighting"
            )
            return

        # Send result
        result_text = format_result(disease, confidence)
        await update.message.reply_text(result_text, parse_mode='Markdown')

        logger.info(f"Prediction: {disease} ({confidence:.1%}) for user {update.effective_user.id}")

    except Exception as e:
        logger.error(f"Photo handling error: {e}")
        await update.message.reply_text(
            "❌ Sorry, something went wrong. Please try again!"
        )


async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle images sent as documents"""
    doc = update.message.document
    if doc.mime_type and doc.mime_type.startswith('image/'):
        await update.message.reply_text("🔬 Analyzing your skin image...")

        try:
            file = await context.bot.get_file(doc.file_id)
            file_bytes = await file.download_as_bytearray()

            disease, confidence = predict_disease(bytes(file_bytes))

            if disease:
                result_text = format_result(disease, confidence)
                await update.message.reply_text(result_text, parse_mode='Markdown')
            else:
                await update.message.reply_text("❌ Could not analyze. Please send a clearer skin photo!")

        except Exception as e:
            logger.error(f"Document handling error: {e}")
            await update.message.reply_text("❌ Error processing image. Please try again!")
    else:
        await update.message.reply_text("📸 Please send a photo/image only!")


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text messages"""
    text = update.message.text.lower()

    if any(word in text for word in ['hi', 'hello', 'hey', 'hii']):
        await update.message.reply_text(
            "👋 Hello! Send me a skin photo and I'll analyze it for you!\n\n📸 Just tap the 📎 icon and send a photo."
        )
    elif any(word in text for word in ['acne', 'pimple']):
        await update.message.reply_text(
            "📸 Send me a photo of the acne and I'll analyze it!\n\nTake a clear, close-up photo in good lighting."
        )
    else:
        await update.message.reply_text(
            "📸 *Send me a skin photo to get started!*\n\nI can detect 7 skin conditions from photos.\n\nType /help for instructions.",
            parse_mode='Markdown'
        )


# ── MAIN ──────────────────────────────────────────────────────────────────────
def main():
    load_model()

    app = Application.builder().token(BOT_TOKEN).build()

    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("about", about_command))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.Document.IMAGE, handle_document))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    logger.info("🚀 MedicusLabs Bot is running!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
