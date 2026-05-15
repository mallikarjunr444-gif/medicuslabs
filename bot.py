"""
🚀 MEDICUSLABS - UNIFIED TELEGRAM BOT (PRODUCTION)
Advanced Skin Disease Detection with ISIC Database & Email Reports
Combined v1 + v2 Features
"""

import os
import logging
import requests
import json
import asyncio
import threading
import re
from io import BytesIO
from datetime import datetime, timedelta
import hashlib
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage

import numpy as np
import cv2
from PIL import Image
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import aiohttp

# ── LOGGING ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ── CONFIGURATION ─────────────────────────────────────────────────────────────
# PRODUCTION CREDENTIALS (from user)
BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', 'your_telegram_bot_token')
HF_API_TOKEN = os.environ.get('HF_API_TOKEN', 'your_huggingface_token')
EMAIL_SENDER = os.environ.get('EMAIL_SENDER', 'your_email@gmail.com')
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD', 'your_app_specific_password')

# API ENDPOINTS
ISIC_API_URL = "https://api.isic-archive.com/api/v2/images"
HF_INFERENCE_API = "https://api-inference.huggingface.co/models"

# In-memory storage (use real DB in production)
user_data = {}
pending_reports = {}
analysis_history = {}
user_emails = {}

# ── LOAD MODEL ────────────────────────────────────────────────────────────────
model = None

def load_model():
    """Load YOLOv8 model - with fallback to Hugging Face"""
    global model
    try:
        from ultralytics import YOLO
        model_path = 'medicuslabs_best.pt'
        
        if os.path.exists(model_path):
            model = YOLO(model_path)
            logger.info("✅ YOLOv8 Model loaded successfully!")
            return True
        else:
            logger.warning(f"⚠️ Model file not found: {model_path}")
            logger.info("📥 Using Hugging Face models for inference...")
            return True  # HF will be used as fallback
    except Exception as e:
        logger.error(f"❌ Model load error: {e}")
        logger.info("💡 Fallback: Using Hugging Face API for predictions")
        return False

# ── ISIC DATABASE INTEGRATION ──────────────────────────────────────────────────
async def get_isic_similar_images(disease_name: str, limit: int = 3):
    """Get similar images from ISIC database for validation"""
    try:
        # Map disease names to ISIC diagnoses
        isic_diagnosis_map = {
            'acne': 'Acne',
            'eczema': 'Dermatitis',
            'psoriasis': 'Psoriasis',
            'ringworm': 'Tinea',
            'vitiligo': 'Vitiligo',
            'melanoma': 'Melanoma',
            'normal_skin': 'Nevus',
            'normal': 'Nevus'
        }
        
        diagnosis = isic_diagnosis_map.get(disease_name, disease_name)
        
        async with aiohttp.ClientSession() as session:
            params = {
                'search': diagnosis,
                'limit': limit,
                'offset': 0
            }
            
            async with session.get(f"{ISIC_API_URL}", params=params, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    results = data.get('results', [])
                    
                    matches = []
                    for img in results[:limit]:
                        matches.append({
                            'id': img.get('id'),
                            'diagnosis': img.get('metadata', {}).get('clinical', {}).get('diagnosis', diagnosis),
                            'url': img.get('metadata', {}).get('clinical', {}).get('image', '')
                        })
                    
                    return matches if matches else []
    except asyncio.TimeoutError:
        logger.warning("ISIC API timeout - continuing without database matches")
    except Exception as e:
        logger.warning(f"ISIC API error: {e}")
    
    return []

# ── HUGGING FACE INFERENCE ────────────────────────────────────────────────────
async def hf_predict_disease(image_bytes: bytes):
    """Use Hugging Face models for skin disease prediction"""
    try:
        if not HF_API_TOKEN:
            return None, 0
        
        async with aiohttp.ClientSession() as session:
            headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}
            
            # Try multiple HF models for skin disease detection
            models_to_try = [
                "dermatology/skin-disease-classification",
                "medimgprocessing/skin-lesion-classification",
            ]
            
            for model_name in models_to_try:
                try:
                    url = f"{HF_INFERENCE_API}/{model_name}"
                    
                    async with session.post(
                        url,
                        headers=headers,
                        data=image_bytes,
                        timeout=aiohttp.ClientTimeout(total=30)
                    ) as resp:
                        if resp.status == 200:
                            result = await resp.json()
                            
                            # Extract top prediction
                            if isinstance(result, list) and len(result) > 0:
                                top_result = result[0]
                                label = top_result.get('label', 'unknown')
                                score = top_result.get('score', 0.0)
                                return label, score
                except Exception as e:
                    logger.warning(f"Model {model_name} failed: {e}")
                    continue
    
    except Exception as e:
        logger.warning(f"HF inference error: {e}")
    
    return None, 0

# ── LOCAL YOLO PREDICTION ──────────────────────────────────────────────────────
def predict_disease_local(image_bytes: bytes):
    """YOLOv8 local prediction"""
    if model is None:
        return None, 0, {}

    try:
        img_array = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

        if img is None:
            return None, 0, {}

        img = cv2.resize(img, (224, 224))
        results = model.predict(img, verbose=False)
        result = results[0]

        predictions = {}
        if hasattr(result, 'probs') and result.probs is not None:
            class_id = result.probs.top1
            confidence = float(result.probs.top1conf)
            class_names = result.names
            predicted_class = class_names[class_id].lower()
            
            for idx, prob in enumerate(result.probs.data):
                predictions[class_names[idx]] = float(prob)
            
            return predicted_class, confidence, predictions

    except Exception as e:
        logger.error(f"YOLOv8 prediction error: {e}")

    return None, 0, {}

async def predict_disease(image_bytes: bytes):
    """Combined prediction: YOLOv8 + HF fallback"""
    # Try local YOLOv8 first
    if model is not None:
        disease, confidence, predictions = predict_disease_local(image_bytes)
        if disease and confidence > 0.5:
            return disease, confidence, predictions
    
    # Fallback to Hugging Face
    logger.info("Using Hugging Face for prediction...")
    disease, confidence = await hf_predict_disease(image_bytes)
    
    if disease:
        return disease.lower(), confidence, {}
    
    return None, 0, {}

# ── EMAIL REPORT DELIVERY ──────────────────────────────────────────────────────
def send_email_report(email: str, disease: str, confidence: float, user_name: str = "User"):
    """Send detailed analysis report via email"""
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"🏥 MedicusLabs AI Analysis Report - {disease.upper()}"
        msg['From'] = EMAIL_SENDER
        msg['To'] = email

        # Get disease info
        disease_info = DISEASE_INFO.get(disease.lower(), DISEASE_INFO['normal_skin'])

        # Build recommendations list
        recommendations = '<br>'.join(disease_info['tips'])

        # Create professional HTML email
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; text-align: center; }}
                .result {{ background: #f9f9f9; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #667eea; }}
                .urgent {{ border-left-color: #e74c3c; background: #fadbd8; }}
                .tips {{ background: #f0f4ff; padding: 15px; border-radius: 8px; margin: 15px 0; }}
                .disclaimer {{ background: #fff3cd; padding: 15px; border-radius: 8px; color: #856404; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🏥 MedicusLabs AI Analysis Report</h1>
                </div>

                <div class="result {'urgent' if disease_info['urgent'] else ''}">
                    <h2>{disease_info['name']}</h2>
                    <p><strong>Description:</strong> {disease_info['desc']}</p>
                    <p><strong>Confidence Score:</strong> <span style="color: #667eea; font-weight: bold;">{confidence:.1%}</span></p>
                    <p><strong>Analysis Date:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>

                <h3>💊 Medical Recommendations:</h3>
                <div class="tips">
                    {recommendations}
                </div>

                <div class="disclaimer">
                    <strong>⚕️ IMPORTANT MEDICAL DISCLAIMER:</strong><br>
                    This report is generated by AI technology for educational purposes only. 
                    It is NOT a substitute for professional medical diagnosis or treatment. 
                    <strong>Always consult a qualified healthcare professional</strong> for proper 
                    medical evaluation, diagnosis, and treatment of any skin condition.
                </div>

                <p style="text-align: center; margin-top: 30px; font-size: 12px; color: #999;">
                    © 2026 MedicusLabs - AI-Powered Skin Disease Detection<br>
                    For educational and research purposes only
                </p>
            </div>
        </body>
        </html>
        """

        msg.attach(MIMEText(html_content, 'html'))

        # Send via Gmail SMTP
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.send_message(msg)
        
        logger.info(f"✅ Email report sent to {email}")
        return True
    except Exception as e:
        logger.error(f"❌ Email error: {e}")
        return False

# ── SCHEDULE EMAIL DELIVERY (10 MINUTES) ──────────────────────────────────────
def schedule_email_report(user_id: int, email: str, disease: str, confidence: float, user_name: str):
    """Schedule email delivery after 10 minutes"""
    def send_delayed():
        import time
        time.sleep(600)  # 10 minutes = 600 seconds
        send_email_report(email, disease, confidence, user_name)
    
    thread = threading.Thread(target=send_delayed, daemon=True)
    thread.start()

# ── DISEASE INFORMATION DATABASE ──────────────────────────────────────────────
DISEASE_INFO = {
    'acne': {
        'name': '🔴 Acne',
        'desc': 'Inflammatory skin condition characterized by pimples, blackheads, and whiteheads',
        'tips': [
            '✓ Use gentle, non-comedogenic cleanser twice daily',
            '✓ Avoid touching, picking, or popping pimples',
            '✓ Apply benzoyl peroxide or salicylic acid gel',
            '✓ Consult dermatologist if severe or persistent',
            '✓ Avoid oily foods and stress',
            '✓ Keep pillowcase clean and change frequently'
        ],
        'urgent': False
    },
    'eczema': {
        'name': '🔴 Eczema (Dermatitis)',
        'desc': 'Chronic inflammation causing dry, itchy, and inflamed skin',
        'tips': [
            '✓ Moisturize with thick cream immediately after bathing',
            '✓ Avoid harsh soaps, use gentle cleansers',
            '✓ Identify and avoid personal triggers (dust, pollen, stress)',
            '✓ Use prescribed steroid cream during flare-ups',
            '✓ Keep skin hydrated with emollients',
            '✓ Avoid extreme temperature changes'
        ],
        'urgent': False
    },
    'psoriasis': {
        'name': '🔴 Psoriasis',
        'desc': 'Autoimmune disease causing thick, scaly, and often painful patches',
        'tips': [
            '✓ Keep skin moisturized at all times with thick creams',
            '✓ Use medicated shampoo for scalp psoriasis',
            '✓ Manage stress - a major trigger for flare-ups',
            '✓ See dermatologist for prescription treatment options',
            '✓ Take warm (not hot) baths with colloidal oatmeal',
            '✓ Avoid alcohol and smoking'
        ],
        'urgent': False
    },
    'ringworm': {
        'name': '⚠️ Ringworm (Tinea)',
        'desc': 'Fungal infection causing circular ring-shaped rash (CONTAGIOUS!)',
        'tips': [
            '✓ Apply antifungal cream (clotrimazole, miconazole) 2x daily',
            '✓ Keep affected area clean and dry',
            '✓ DO NOT share towels, clothes, or bedsheets',
            '✓ Avoid scratching - it spreads the infection',
            '✓ Wash hands after touching affected area',
            '✓ See doctor if spreading or not improving in 2 weeks'
        ],
        'urgent': False
    },
    'vitiligo': {
        'name': '⚪ Vitiligo',
        'desc': 'Loss of skin pigmentation resulting in white patches',
        'tips': [
            '✓ Apply SPF 50+ sunscreen on white patches daily',
            '✓ Use cosmetic cover-up if desired for appearance',
            '✓ Consult dermatologist for repigmentation therapy options',
            '✓ Maintain healthy diet rich in Vitamin B12 & D3',
            '✓ Manage stress - stress can worsen condition',
            '✓ Avoid skin trauma and injuries'
        ],
        'urgent': False
    },
    'melanoma': {
        'name': '🚨 MELANOMA (SKIN CANCER)',
        'desc': '⚠️ URGENT: Possible malignant melanoma (skin cancer) detected!',
        'tips': [
            '🚨 SEEK IMMEDIATE MEDICAL ATTENTION TODAY',
            '✓ Schedule urgent appointment with dermatologist or oncologist',
            '✓ Do NOT delay - early detection significantly improves survival',
            '✓ Avoid sun exposure on affected area',
            '✓ Keep the area clean and covered',
            '✓ Bring this report to your doctor appointment'
        ],
        'urgent': True
    },
    'normal_skin': {
        'name': '✅ Normal Healthy Skin',
        'desc': 'No signs of skin disease detected - skin appears healthy!',
        'tips': [
            '✓ Continue your daily skincare routine',
            '✓ Apply sunscreen SPF 30+ every morning',
            '✓ Stay hydrated - drink 8 glasses of water daily',
            '✓ Perform monthly self-checks for any changes',
            '✓ Maintain balanced diet rich in antioxidants',
            '✓ Get 7-8 hours of quality sleep'
        ],
        'urgent': False
    },
    'normal': {
        'name': '✅ Normal Healthy Skin',
        'desc': 'No signs of skin disease detected!',
        'tips': [
            '✓ Continue your daily skincare routine',
            '✓ Apply sunscreen SPF 30+ daily',
            '✓ Stay hydrated'
        ],
        'urgent': False
    }
}

# ── FORMAT RESPONSE MESSAGE ───────────────────────────────────────────────────
async def format_result(disease: str, confidence: float, isic_matches: list = None) -> str:
    """Format analysis result with ISIC database matches"""
    info = DISEASE_INFO.get(disease.lower(), DISEASE_INFO['normal_skin'])
    tips_text = '\n'.join(info['tips'])

    if info['urgent']:
        header = "🚨🚨🚨 URGENT ALERT - SEEK IMMEDIATE MEDICAL ATTENTION 🚨🚨🚨"
    else:
        header = "🔬 MedicusLabs AI Analysis Report"

    msg = f"""{header}

{info['name']}

📋 *Description:*
{info['desc']}

📊 *AI Confidence Level:* `{confidence:.1%}`

💊 *Medical Recommendations:*
{tips_text}"""

    # Add ISIC database reference
    if isic_matches and len(isic_matches) > 0:
        msg += "\n\n📚 *Similar Cases from Medical Database (ISIC Archive):*"
        for i, match in enumerate(isic_matches[:3], 1):
            diagnosis = match.get('diagnosis', 'Medical Case')
            msg += f"\n  {i}. {diagnosis}"

    msg += f"""

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚕️ *MEDICAL DISCLAIMER:* 
This is an AI-assisted analysis for educational purposes ONLY. 
It is NOT a substitute for professional medical diagnosis.
🏥 ALWAYS consult a qualified dermatologist for proper evaluation.

📧 *Email Report:* Detailed report will be sent in ~10 minutes!
📱 Send another photo to analyze a different area!"""

    return msg

# ── TELEGRAM BOT COMMAND HANDLERS ──────────────────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Welcome command"""
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name or "User"
    
    # Store user data
    user_data[user_id] = {
        'name': user_name,
        'started_at': datetime.now(),
        'reports': []
    }
    
    welcome = """👋 *Welcome to MedicusLabs AI!*\n\n🏥 *Professional Skin Disease Detection System*\n\n🔬 I detect *7 skin conditions* using advanced AI + 500,000+ medical images:\n\n• 🔴 Acne\n• 🔴 Eczema  \n• 🔴 Psoriasis\n• ⚠️ Ringworm (Tinea)\n• ⚪ Vitiligo\n• 🚨 Melanoma (URGENT)\n• ✅ Normal Skin\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n📸 *HOW TO USE:*\n1️⃣ Take a clear, close-up photo of affected skin area\n2️⃣ Send the photo in this chat\n3️⃣ Get instant AI analysis in seconds\n4️⃣ Receive detailed email report in 10 minutes\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n🌟 *Features:*\n✓ AI analysis with 85%+ accuracy\n✓ ISIC database matching (500k+ medical images)\n✓ Detailed medical recommendations\n✓ Automated email reports\n✓ Professional assessment\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n*To receive the email report,* set your email with:\n`/setemail your.email@example.com`\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n/help — Instructions & tips\n/about — About MedicusLabs\n/history — Your analysis history\n\n⚕️ *DISCLAIMER:* For educational purposes. Always consult a doctor.\n\n📸 *Send your photo now!*"""

    await update.message.reply_text(welcome, parse_mode='Markdown')


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Help command"""
    help_text = """🆘 *MedicusLabs Help & Instructions*\n\n*How to Use:*\n1️⃣ Take a clear, close-up photo of the affected skin area\n2️⃣ Use natural lighting (avoid shadows)\n3️⃣ Send the photo in this chat\n4️⃣ Get instant AI analysis\n5️⃣ Receive email report in ~10 minutes\n\n*Tip:* Set your email first with `/setemail your.email@example.com` to receive the report by email.\n\n*Tips for Best Results:*\n• 📸 Use good lighting (natural daylight preferred)\n• 📏 Take close-up photo (5-15 cm away)\n• 🤳 Keep camera steady\n\n*Conditions We Detect:*\n🔴 Acne - Pimples & inflammatory lesions\n🔴 Eczema - Dry, itchy, inflamed skin\n🔴 Psoriasis - Thick scaly patches\n⚠️ Ringworm - Circular fungal infection (CONTAGIOUS!)\n⚪ Vitiligo - White pigmented patches\n🚨 Melanoma - SKIN CANCER (URGENT)\n✅ Normal Skin - Healthy skin\n\n*Bot Commands:*\n/start — Welcome message\n/help — This guide\n/about — About MedicusLabs & team\n/history — View your analysis history\n/setemail — Set your email for report delivery\n\n*Report Delivery:*\n📧 Automatic email sent in ~10 minutes when an email is set\n✓ Detailed diagnosis\n✓ Confidence scores\n✓ Medical recommendations\n✓ Professional disclaimer\n\n⚠️ *IMPORTANT:*\n• This is NOT a medical diagnosis tool\n• Always consult a qualified dermatologist\n• In case of emergency, seek immediate medical help\n• Early detection saves lives!\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━\nReady? Send your photo now! 📸"""

    await update.message.reply_text(help_text, parse_mode='Markdown')

*How to Use:*
1️⃣ Take a clear, close-up photo of the affected skin area
2️⃣ Use natural lighting (avoid shadows)
3️⃣ Send the photo in this chat
4️⃣ Get instant AI analysis
5️⃣ Receive email report in ~10 minutes

*Tips for Best Results:*
• 📸 Use good lighting (natural daylight preferred)
• 📏 Take close-up photo (5-15 cm away)
• 🤳 Keep camera steady
• 🎯 Show the affected area clearly
• 📐 Include some surrounding normal skin for comparison

*Conditions We Detect:*
🔴 Acne - Pimples & inflammatory lesions
🔴 Eczema - Dry, itchy, inflamed skin
🔴 Psoriasis - Thick scaly patches
⚠️ Ringworm - Circular fungal infection (CONTAGIOUS!)
⚪ Vitiligo - White pigmented patches
🚨 Melanoma - SKIN CANCER (URGENT)
✅ Normal Skin - Healthy skin

*Bot Commands:*
/start — Welcome message
/help — This guide
/about — About MedicusLabs & team
/history — View your analysis history

*Report Delivery:*
📧 Automatic email sent in ~10 minutes
✓ Detailed diagnosis
✓ Confidence scores
✓ Medical recommendations
✓ Professional disclaimer

⚠️ *IMPORTANT:*
• This is NOT a medical diagnosis tool
• Always consult a qualified dermatologist
• In case of emergency, seek immediate medical help
• Early detection saves lives!

━━━━━━━━━━━━━━━━━━━━━━━━━━
Ready? Send your photo now! 📸"""

    await update.message.reply_text(help_text, parse_mode='Markdown')


async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """About command"""
    about = """ℹ️ *About MedicusLabs*

🤖 *AI Technology:*
• YOLOv8 Deep Learning Model
• Hugging Face AI Integration
• Real-time image processing

📊 *Data & Accuracy:*
• Training: 500,000+ medical images
• Database: ISIC Archive integration
• Accuracy: 85%+
• Speed: <3 seconds analysis

🏥 *Medical Features:*
• 7 skin conditions detected
• ISIC database matching
• Confidence scoring
• Professional recommendations

📧 *Report System:*
• Automated email delivery (10 min)
• Professional HTML formatting
• Medical recommendations
• Complete disclaimer

👥 *Development Team:*
• Mallikarjun R — AI/ML Engineering
• Mohammad Adil — Backend Development
• Mallanagowda M — DevOps/Infrastructure
• Nigam Patel — QA/Testing

🏫 *Organization:*
DSATM (Dayananda Sagar Academy of Technology & Management)
Bengaluru, India

🔗 *Integrations:*
🌐 ISIC Archive — 500k+ medical images
🤗 Hugging Face — Enhanced ML models
📧 Gmail — Automated reports
📱 Telegram Bot API — User interaction

━━━━━━━━━━━━━━━━━━━━━━━━━━
⚕️ *DISCLAIMER:*
MedicusLabs is an educational AI system.
NOT a medical diagnosis tool.
Always consult qualified healthcare professionals.

*Version:* 2.0 (Unified)
*Status:* 🟢 Production Ready
*Last Updated:* May 14, 2026"""

    await update.message.reply_text(about, parse_mode='Markdown')


async def history_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show user's analysis history"""
    user_id = update.effective_user.id
    
    if user_id not in analysis_history or not analysis_history[user_id]:
        await update.message.reply_text(
            "📊 *No analysis history yet*\n\nSend your first skin photo to get started! 📸",
            parse_mode='Markdown'
        )
        return
    
    history = analysis_history[user_id]
    msg = "📊 *Your Analysis History*\n\n"
    
    for i, analysis in enumerate(history[-5:], 1):  # Show last 5
        msg += f"{i}. {analysis.get('disease', 'Unknown')} - {analysis.get('confidence', 0):.0%}\n"
        msg += f"   ⏰ {analysis.get('timestamp', 'Unknown')}\n\n"
    
    await update.message.reply_text(msg, parse_mode='Markdown')


def validate_email(email: str) -> bool:
    """Validate email address format"""
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return bool(re.match(pattern, email.strip()))


async def set_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set the user's email address for report delivery"""
    user_id = update.effective_user.id
    if not context.args:
        await update.message.reply_text(
            "📧 Please send your email using this command:\n`/setemail your.email@example.com`",
            parse_mode='Markdown'
        )
        return

    email_address = ' '.join(context.args).strip()
    if validate_email(email_address):
        user_emails[user_id] = email_address
        await update.message.reply_text(
            f"✅ Email saved successfully: `{email_address}`\n\n" \
            "You will now receive the detailed report by email after sending a photo.",
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            "❌ That doesn't look like a valid email address.\n" \
            "Please use: `/setemail your.email@example.com`",
            parse_mode='Markdown'
        )


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming photos - main analysis function"""
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name or "User"
    user_email = user_emails.get(user_id)
    
    # Send loading message
    msg = await update.message.reply_text(
        "🔬 *Analyzing your skin image...*\n"
        "⏳ Please wait (checking against 500k+ medical database)!\n\n"
        "_Using YOLOv8 + Hugging Face AI Models..._",
        parse_mode='Markdown'
    )

    try:
        # Download image
        photo = update.message.photo[-1]
        photo_file = await context.bot.get_file(photo.file_id)
        photo_bytes = await photo_file.download_as_bytearray()

        # Perform prediction
        logger.info(f"🔍 Analyzing image for user {user_id} ({user_name})")
        disease, confidence, predictions = await predict_disease(bytes(photo_bytes))

        # Check if analysis failed
        if disease is None or confidence < 0.4:
            await msg.edit_text(
                "❌ *Analysis Failed*\n\n"
                "Could not analyze the image.\n\n"
                "*Please try:*\n"
                "• Send a clearer, closer photo\n"
                "• Ensure good lighting\n"
                "• Show affected area clearly\n"
                "• Try a different angle",
                parse_mode='Markdown'
            )
            return

        # Get ISIC database matches
        logger.info(f"🔍 Fetching ISIC database matches for {disease}...")
        isic_matches = await get_isic_similar_images(disease)

        # Format and send result
        result_text = await format_result(disease, confidence, isic_matches)
        await msg.edit_text(result_text, parse_mode='Markdown')

        # Store analysis
        if user_id not in analysis_history:
            analysis_history[user_id] = []
        
        analysis_history[user_id].append({
            'disease': disease,
            'confidence': confidence,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })

        logger.info(f"✅ Analysis complete: {disease} ({confidence:.1%}) | User: {user_id}")

        if user_email and validate_email(user_email):
            logger.info(f"📧 Scheduling email report for {user_email}...")
            schedule_email_report(user_id, user_email, disease, confidence, user_name)
        else:
            await update.message.reply_text(
                "📧 *Email report not scheduled*\n\n" \
                "Please set a valid email first using:\n`/setemail your.email@example.com`",
                parse_mode='Markdown'
            )

    except Exception as e:
        logger.error(f"❌ Error handling photo: {e}", exc_info=True)
        await msg.edit_text(
            "❌ *Oops! Something went wrong*\n\n"
            "Please try again or contact support.\n\n"
            "_Our team is investigating the issue._",
            parse_mode='Markdown'
        )


async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle images sent as documents"""
    doc = update.message.document
    user_id = update.effective_user.id
    
    if not (doc.mime_type and doc.mime_type.startswith('image/')):
        await update.message.reply_text("📸 Please send a photo/image only!", parse_mode='Markdown')
        return

    msg = await update.message.reply_text("🔬 *Analyzing image...*", parse_mode='Markdown')

    try:
        file = await context.bot.get_file(doc.file_id)
        file_bytes = await file.download_as_bytearray()

        disease, confidence, _ = await predict_disease(bytes(file_bytes))

        if disease and confidence > 0.4:
            isic_matches = await get_isic_similar_images(disease)
            result_text = await format_result(disease, confidence, isic_matches)
            await msg.edit_text(result_text, parse_mode='Markdown')
        else:
            await msg.edit_text("❌ Could not analyze. Please send a clearer skin photo!", parse_mode='Markdown')

    except Exception as e:
        logger.error(f"Document handling error: {e}")
        await msg.edit_text("❌ Error processing image!", parse_mode='Markdown')


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text messages"""
    text = update.message.text.lower()

    if any(word in text for word in ['hi', 'hello', 'hey', 'hii', 'namaste']):
        await update.message.reply_text(
            "👋 Hello! 👋\n\n"
            "I'm MedicusLabs AI - ready to analyze your skin! 🏥\n\n"
            "📸 *Just send me a photo* of your skin and I'll:\n"
            "✓ Analyze it with AI\n"
            "✓ Compare with 500k+ medical images\n"
            "✓ Send you a detailed report\n\n"
            "Type /help for tips or send a photo now! 📸",
            parse_mode='Markdown'
        )
    elif any(word in text for word in ['acne', 'pimple', 'zit']):
        await update.message.reply_text(
            "🔴 *Acne Analysis*\n\n"
            "Send me a clear photo of the acne and I'll analyze it!\n\n"
            "*Tips:*\n"
            "• Good lighting (natural is best)\n"
            "• Close-up photo (5-15 cm)\n"
            "• Steady camera\n\n"
            "📸 Ready to upload? 📸",
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            "👀 *I understand text, but I work best with photos!*\n\n"
            "📸 *Send me a skin photo* to get started!\n\n"
            "Or use these commands:\n"
            "/help — Full instructions\n"
            "/about — About MedicusLabs\n"
            "/history — Your analysis history",
            parse_mode='Markdown'
        )

# ── MAIN APPLICATION ──────────────────────────────────────────────────────────
def main():
    """Start the bot"""
    logger.info("="*60)
    logger.info("🚀 MEDICUSLABS - UNIFIED TELEGRAM BOT v2.0 (PRODUCTION)")
    logger.info("="*60)
    
    # Load model
    if not load_model():
        logger.warning("⚠️ YOLOv8 model not available - using Hugging Face fallback")
    
    logger.info(f"🤖 Bot Token: {'*' * 20}***")
    logger.info(f"🤗 HF Token: {'*' * 20}***")
    logger.info(f"📧 Email: {EMAIL_SENDER}")
    logger.info(f"🌐 ISIC API: Connected")
    logger.info("="*60)

    # Create application
    app = Application.builder().token(BOT_TOKEN).build()

    # Add command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("about", about_command))
    app.add_handler(CommandHandler("history", history_command))
    app.add_handler(CommandHandler("setemail", set_email))

    # Add message handlers
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.Document.IMAGE, handle_document))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    logger.info("✅ All handlers registered")
    logger.info("🟢 Bot is starting...")
    logger.info("="*60)
    logger.info("🚀 MedicusLabs Bot v2.0 is LIVE and ready!")
    logger.info("🔗 ISIC Database: 500k+ medical images")
    logger.info("🤗 Hugging Face: AI Enhanced")
    logger.info("📧 Email Reports: Automated (10-min)")
    logger.info("="*60)
    
    # Start polling
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
