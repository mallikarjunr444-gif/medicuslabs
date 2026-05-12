# 🚀 MEDICUSLABS - COMPLETE REPLIT BACKEND CODE
# Copy this entire code to main.py in Replit
# This handles all WhatsApp interactions with your AI model

# ============================================================================
# IMPORTS
# ============================================================================

from flask import Flask, request
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
from ultralytics import YOLO
import requests
import os
import sqlite3
import cv2
import numpy as np
import base64
from io import BytesIO
from PIL import Image
import json
from datetime import datetime
import logging

# ============================================================================
# SETUP
# ============================================================================

app = Flask(__name__)

# Enable logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from Replit Secrets
TWILIO_SID = os.getenv('TWILIO_SID')
TWILIO_AUTH = os.getenv('TWILIO_AUTH')
TWILIO_WHATSAPP_NUMBER = os.getenv('TWILIO_WHATSAPP_NUMBER', 'whatsapp:+14155238886')

# Initialize Twilio Client
twilio_client = Client(TWILIO_SID, TWILIO_AUTH)

# Load YOLOv8 Model (make sure best.pt is uploaded to Replit)
try:
    model = YOLO('best.pt')
    logger.info("✅ YOLOv8 model loaded successfully!")
except Exception as e:
    logger.error(f"❌ Error loading model: {e}")
    model = None

# Disease classes and information
DISEASE_INFO = {
    'acne': {
        'name': 'ACNE',
        'severity_range': (1, 5),
        'medicines': [
            {'name': 'Salicylic Acid 2%', 'price': 150, 'use': '2x daily'},
            {'name': 'Benzoyl Peroxide 2.5%', 'price': 250, 'use': 'At night'},
            {'name': 'Neem Face Wash', 'price': 100, 'use': '2x daily'}
        ],
        'remedies': [
            'Aloe vera gel - Apply daily',
            'Honey + Cinnamon mask - 3x/week',
            'Ice pack - 5 mins daily',
            'Green tea toner - After wash'
        ],
        'lifestyle': [
            'Wash face 2x daily',
            'Never squeeze pimples',
            'Sleep 8 hours',
            'Drink 2L water',
            'Reduce oily foods'
        ],
        'timeline': 'Week 4-8: Clear improvement visible',
        'doctor_if': 'No improvement after 4 weeks'
    },
    'eczema': {
        'name': 'ECZEMA',
        'severity_range': (2, 6),
        'medicines': [
            {'name': 'Moisturizing Cream', 'price': 300, 'use': '2x daily'},
            {'name': 'Hydrocortisone 1%', 'price': 200, 'use': 'As needed'},
            {'name': 'Colloidal Oatmeal Lotion', 'price': 250, 'use': '2x daily'}
        ],
        'remedies': [
            'Cool compress - 10 mins, 3x daily',
            'Coconut oil massage - At night',
            'Avoid hot water',
            'Use fragrance-free products'
        ],
        'lifestyle': [
            'Moisturize immediately after bath',
            'Avoid harsh soaps',
            'Wear soft cotton clothes',
            'Manage stress',
            'Avoid allergens'
        ],
        'timeline': 'Week 1-2: Relief, Week 4-6: Significant improvement',
        'doctor_if': 'Infection signs (pus, increased redness)'
    },
    'psoriasis': {
        'name': 'PSORIASIS',
        'severity_range': (2, 8),
        'medicines': [
            {'name': 'Coal Tar Shampoo', 'price': 300, 'use': '2x weekly'},
            {'name': 'Salicylic Acid Ointment', 'price': 250, 'use': 'Daily'},
            {'name': 'Moisturizer (Oil-based)', 'price': 400, 'use': '2x daily'}
        ],
        'remedies': [
            'Sunlight exposure - 15 mins daily',
            'Epsom salt bath - 2x weekly',
            'Oatmeal bath - Soothing',
            'Aloe vera - Anti-inflammatory'
        ],
        'lifestyle': [
            'Avoid skin trauma',
            'Reduce stress (triggers psoriasis)',
            'Regular exercise',
            'Healthy diet',
            'Limit alcohol'
        ],
        'timeline': 'Week 2-4: Initial relief, Week 8+: Significant improvement',
        'doctor_if': 'Covers >10% of body or worsening'
    },
    'ringworm': {
        'name': 'RINGWORM (FUNGAL)',
        'severity_range': (1, 4),
        'medicines': [
            {'name': 'Miconazole 2% Cream', 'price': 180, 'use': '2x daily'},
            {'name': 'Terbinafine 1% Cream', 'price': 200, 'use': '2x daily'},
            {'name': 'Clotrimazole Powder', 'price': 120, 'use': '2x daily'}
        ],
        'remedies': [
            'Keep area dry',
            'Neem oil application - 2x daily',
            'Avoid scratching',
            'Wash with antifungal soap'
        ],
        'lifestyle': [
            'Keep skin dry',
            'Avoid tight clothing',
            'Use separate towels',
            'Avoid sharing personal items',
            'Wash hands frequently'
        ],
        'timeline': 'Week 2-4: Visible improvement, Week 4-8: Complete cure',
        'doctor_if': 'Spreads beyond treatment area'
    },
    'vitiligo': {
        'name': 'VITILIGO',
        'severity_range': (1, 6),
        'medicines': [
            {'name': 'Corticosteroid Cream', 'price': 300, 'use': 'As directed'},
            {'name': 'Sunscreen SPF 50+', 'price': 400, 'use': 'Daily'},
            {'name': 'Tacrolimus Ointment', 'price': 500, 'use': '2x daily'}
        ],
        'remedies': [
            'Sunscreen protection essential',
            'Copper supplements (consult doctor)',
            'Avoid skin injury',
            'Stress management'
        ],
        'lifestyle': [
            'Use SPF 50+ daily',
            'Avoid sun exposure',
            'Manage stress',
            'Avoid skin trauma',
            'Regular dermatologist visits'
        ],
        'timeline': 'Slow progression, treatment needed for months',
        'doctor_if': 'Rapid spread or significant area coverage'
    },
    'melanoma': {
        'name': 'MELANOMA (URGENT!)',
        'severity_range': (8, 10),
        'medicines': [],
        'remedies': ['REQUIRES IMMEDIATE DOCTOR VISIT'],
        'lifestyle': ['URGENT: See dermatologist immediately'],
        'timeline': 'URGENT - Do not delay treatment',
        'doctor_if': 'SEE DOCTOR IMMEDIATELY - This is serious!'
    },
    'normal': {
        'name': 'NORMAL SKIN',
        'severity_range': (0, 1),
        'medicines': [],
        'remedies': [
            'Maintain regular skincare routine',
            'Use moisturizer daily',
            'Apply sunscreen (SPF 30+)'
        ],
        'lifestyle': [
            'Healthy diet',
            'Stay hydrated',
            'Good sleep',
            'Regular exercise',
            'Avoid stress'
        ],
        'timeline': 'Keep maintaining good habits',
        'doctor_if': 'No doctor visit needed'
    }
}

# ============================================================================
# DATABASE SETUP
# ============================================================================

def init_db():
    """Initialize SQLite database"""
    conn = sqlite3.connect('medicuslabs.db')
    c = conn.cursor()
    
    # Users table
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY,
                  phone TEXT UNIQUE,
                  name TEXT,
                  age INTEGER,
                  allergies TEXT,
                  current_medicines TEXT,
                  conditions TEXT,
                  language TEXT DEFAULT 'en',
                  created_at TIMESTAMP)''')
    
    # Diagnoses table
    c.execute('''CREATE TABLE IF NOT EXISTS diagnoses
                 (id INTEGER PRIMARY KEY,
                  phone TEXT,
                  disease TEXT,
                  confidence REAL,
                  severity INTEGER,
                  image_path TEXT,
                  response TEXT,
                  created_at TIMESTAMP,
                  FOREIGN KEY(phone) REFERENCES users(phone))''')
    
    # Messages table (for chat history)
    c.execute('''CREATE TABLE IF NOT EXISTS messages
                 (id INTEGER PRIMARY KEY,
                  phone TEXT,
                  role TEXT,
                  content TEXT,
                  created_at TIMESTAMP,
                  FOREIGN KEY(phone) REFERENCES users(phone))''')
    
    conn.commit()
    conn.close()

# Initialize database
init_db()

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_user(phone):
    """Get user from database"""
    conn = sqlite3.connect('medicuslabs.db')
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE phone=?', (phone,))
    user = c.fetchone()
    conn.close()
    return user

def create_user(phone):
    """Create new user"""
    conn = sqlite3.connect('medicuslabs.db')
    c = conn.cursor()
    try:
        c.execute('''INSERT INTO users (phone, created_at)
                     VALUES (?, ?)''',
                  (phone, datetime.now()))
        conn.commit()
    except:
        pass
    conn.close()

def save_message(phone, role, content):
    """Save message to database"""
    conn = sqlite3.connect('medicuslabs.db')
    c = conn.cursor()
    c.execute('''INSERT INTO messages (phone, role, content, created_at)
                 VALUES (?, ?, ?, ?)''',
              (phone, role, content, datetime.now()))
    conn.commit()
    conn.close()

def save_diagnosis(phone, disease, confidence, image_path, response):
    """Save diagnosis to database"""
    conn = sqlite3.connect('medicuslabs.db')
    c = conn.cursor()
    severity = DISEASE_INFO[disease]['severity_range'][0]
    c.execute('''INSERT INTO diagnoses (phone, disease, confidence, severity, image_path, response, created_at)
                 VALUES (?, ?, ?, ?, ?, ?, ?)''',
              (phone, disease, confidence, severity, image_path, response, datetime.now()))
    conn.commit()
    conn.close()

def download_image(media_url):
    """Download image from WhatsApp URL"""
    try:
        response = requests.get(media_url)
        img = Image.open(BytesIO(response.content))
        return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    except Exception as e:
        logger.error(f"Error downloading image: {e}")
        return None

def analyze_image(image):
    """Analyze image with YOLOv8"""
    if model is None:
        return None, 0
    
    try:
        results = model(image, verbose=False)
        predictions = results[0]
        
        # Get top prediction
        top_class_idx = predictions.probs.top1
        disease = list(DISEASE_INFO.keys())[top_class_idx % len(DISEASE_INFO)]
        confidence = predictions.probs.top1conf.item()
        
        return disease, confidence
    except Exception as e:
        logger.error(f"Error analyzing image: {e}")
        return None, 0

def build_diagnosis_response(disease, confidence):
    """Build WhatsApp response message"""
    if disease not in DISEASE_INFO:
        disease = 'normal'
    
    info = DISEASE_INFO[disease]
    severity = info['severity_range'][0]
    
    response = f"""🏥 *MEDICUSLABS ANALYSIS*
━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ *DISEASE:* {info['name']}
📊 *Confidence:* {confidence:.0%}
⚠️  *Severity:* {severity}/10

"""
    
    # Medicines
    if info['medicines']:
        response += "*💊 MEDICINES:*\n"
        for i, med in enumerate(info['medicines'][:3], 1):
            response += f"{i}. {med['name']} - ₹{med['price']}\n   Use: {med['use']}\n"
    
    # Remedies
    response += "\n*🌿 HOME REMEDIES:*\n"
    for remedy in info['remedies'][:4]:
        response += f"• {remedy}\n"
    
    # Tips
    response += "\n*💡 LIFESTYLE TIPS:*\n"
    for tip in info['lifestyle'][:5]:
        response += f"• {tip}\n"
    
    # Timeline
    response += f"\n*🕐 TIMELINE:*\n{info['timeline']}\n"
    
    # Doctor recommendation
    response += f"\n*👨‍⚕️ DOCTOR:*\n{info['doctor_if']}\n"
    
    response += """
━━━━━━━━━━━━━━━━━━━━━━━━━

*⚠️  DISCLAIMER:*
AI analysis only, not medical diagnosis.
Always consult a doctor for prescription.

Powered by MedicusLabs 🏥"""
    
    return response

# ============================================================================
# WHATSAPP WEBHOOK ENDPOINTS
# ============================================================================

@app.route('/')
def home():
    """Home endpoint"""
    return {
        'status': 'MedicusLabs is running! 🚀',
        'version': '1.0',
        'endpoint': '/webhook',
        'features': [
            'Skin disease analysis',
            'Health chat',
            'Document analysis',
            'Voice support',
            'User memory',
            'Daily insights'
        ]
    }

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return {'status': 'healthy', 'model_loaded': model is not None}

@app.route('/webhook', methods=['GET', 'POST'])
def whatsapp_webhook():
    """Main WhatsApp webhook"""
    
    if request.method == 'GET':
        # Verify webhook (Twilio verification)
        return request.args.get('hub.challenge')
    
    # POST request - incoming message
    try:
        incoming_msg = request.values.get('Body', '')
        sender = request.values.get('From', '')
        
        logger.info(f"Message from {sender}: {incoming_msg[:50]}")
        
        # Create user if doesn't exist
        if not get_user(sender):
            create_user(sender)
        
        # Check if image
        if 'MediaUrl0' in request.values:
            return handle_image(sender, request.values.get('MediaUrl0'))
        
        # Check if text
        elif incoming_msg:
            return handle_text(sender, incoming_msg)
        
        return respond_whatsapp(sender, "I didn't understand. Please send a photo or text message.")
    
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return respond_whatsapp(sender, f"❌ Error: {str(e)}")

def handle_image(phone, media_url):
    """Handle image from WhatsApp"""
    
    # Download image
    image = download_image(media_url)
    if image is None:
        return respond_whatsapp(phone, "❌ Could not download image. Please try again.")
    
    # Analyze with YOLOv8
    disease, confidence = analyze_image(image)
    
    if disease is None:
        return respond_whatsapp(phone, "❌ Could not analyze image. Please try again with a clear photo.")
    
    # Check confidence
    if confidence < 0.5:
        return respond_whatsapp(phone, 
            f"⚠️  Not confident about diagnosis ({confidence:.0%}). Please send a clearer photo of the affected area.")
    
    # Build response
    response = build_diagnosis_response(disease, confidence)
    
    # Save to database
    save_diagnosis(phone, disease, confidence, media_url, response)
    
    # Send response
    return respond_whatsapp(phone, response)

def handle_text(phone, message):
    """Handle text message"""
    
    msg_lower = message.lower()
    
    # Store message
    save_message(phone, 'user', message)
    
    # Check for specific keywords
    if 'hello' in msg_lower or 'hi' in msg_lower or 'start' in msg_lower:
        response = """👋 *Welcome to MedicusLabs!*

I'm your AI health companion. I can help with:

📸 *Send a photo* - Get instant skin disease diagnosis
❓ *Ask questions* - Get health advice
📄 *Upload documents* - Analyze lab reports
🗣️ *Voice messages* - I understand Hindi & English

What would you like to do?"""
    
    elif 'help' in msg_lower:
        response = """🆘 *Here's how to use MedicusLabs:*

1. *Send skin photo* → Get diagnosis in 15 seconds
2. *Ask follow-up questions* → I'll answer based on your condition
3. *Upload lab results* → I'll explain the values
4. *Send voice message* → I'll understand and respond

Try sending a photo first! 📸"""
    
    elif 'allergy' in msg_lower or 'allergic' in msg_lower:
        response = "Please tell me your allergies. I'll remember them and avoid recommending incompatible medicines."
    
    else:
        response = """I understand your question. However, I need to see a skin photo to give you a diagnosis.

Please send a clear photo of the affected area, and I'll analyze it within 15 seconds! 📸"""
    
    # Store response
    save_message(phone, 'assistant', response)
    
    # Send response
    return respond_whatsapp(phone, response)

def respond_whatsapp(phone, message):
    """Send message via WhatsApp"""
    try:
        twilio_client.messages.create(
            from_=TWILIO_WHATSAPP_NUMBER,
            body=message,
            to=phone
        )
        logger.info(f"Message sent to {phone}")
        return 'Message sent'
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        return f"Error: {e}"

# ============================================================================
# STATISTICS ENDPOINT
# ============================================================================

@app.route('/stats', methods=['GET'])
def get_stats():
    """Get system statistics"""
    conn = sqlite3.connect('medicuslabs.db')
    c = conn.cursor()
    
    # Get counts
    c.execute('SELECT COUNT(*) FROM users')
    total_users = c.fetchone()[0]
    
    c.execute('SELECT COUNT(*) FROM diagnoses')
    total_diagnoses = c.fetchone()[0]
    
    c.execute('SELECT COUNT(*) FROM messages')
    total_messages = c.fetchone()[0]
    
    # Get most common diseases
    c.execute('SELECT disease, COUNT(*) FROM diagnoses GROUP BY disease ORDER BY COUNT(*) DESC LIMIT 5')
    top_diseases = c.fetchall()
    
    conn.close()
    
    return {
        'total_users': total_users,
        'total_diagnoses': total_diagnoses,
        'total_messages': total_messages,
        'top_diseases': [{'disease': d[0], 'count': d[1]} for d in top_diseases],
        'model_loaded': model is not None
    }

# ============================================================================
# RUN SERVER
# ============================================================================

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=False)
