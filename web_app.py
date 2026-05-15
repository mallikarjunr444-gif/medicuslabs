"""
🌐 MEDICUSLABS - WEB DASHBOARD
Email signup + Image upload + Report delivery
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import os
import json
import cv2
import numpy as np
from io import BytesIO
import threading
import requests
from PIL import Image

# ── FLASK APP SETUP ──────────────────────────────────────────────────────────
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'medicuslabs-secret-2024')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL', 
    'sqlite:///medicuslabs.db'
)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

# ── EMAIL CONFIGURATION ──────────────────────────────────────────────────────
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('EMAIL_SENDER')
app.config['MAIL_PASSWORD'] = os.environ.get('EMAIL_PASSWORD')

db = SQLAlchemy(app)
mail = Mail(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Create uploads folder
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# ── DATABASE MODELS ──────────────────────────────────────────────────────────
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200))
    name = db.Column(db.String(120))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    reports = db.relationship('Report', backref='user', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    disease = db.Column(db.String(100))
    confidence = db.Column(db.Float)
    image_path = db.Column(db.String(255))
    analysis_data = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    sent_at = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='pending')  # pending, sent, viewed

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ── DISEASE INFO ──────────────────────────────────────────────────────────────
DISEASE_INFO = {
    'acne': {
        'name': '🔴 Acne',
        'desc': 'Inflammatory skin condition with pimples & spots',
        'tips': [
            'Use gentle, non-comedogenic cleanser twice daily',
            'Avoid touching or popping pimples',
            'Apply benzoyl peroxide or salicylic acid gel',
            'Consult dermatologist if severe',
        ]
    },
    'eczema': {
        'name': '🔴 Eczema',
        'desc': 'Chronic inflammation causing dry, itchy skin',
        'tips': [
            'Moisturize with thick cream immediately after bathing',
            'Avoid soap, use gentle cleansers',
            'Identify & avoid triggers',
            'Use prescribed steroid cream for flare-ups',
        ]
    },
    'psoriasis': {
        'name': '🔴 Psoriasis',
        'desc': 'Autoimmune disease causing thick scaly patches',
        'tips': [
            'Keep skin moisturized at all times',
            'Use medicated shampoo for scalp psoriasis',
            'Manage stress',
            'See dermatologist for treatment',
        ]
    },
    'ringworm': {
        'name': '⚠️ Ringworm (Tinea)',
        'desc': 'Fungal infection — circular rash (CONTAGIOUS!)',
        'tips': [
            'Apply antifungal cream twice daily',
            'Keep affected area clean and dry',
            'Do NOT share towels or clothes',
            'Avoid scratching',
        ]
    },
    'vitiligo': {
        'name': '⚪ Vitiligo',
        'desc': 'Loss of skin pigmentation (white patches)',
        'tips': [
            'Apply SPF 50+ sunscreen on patches daily',
            'Consider cosmetic cover-up',
            'Consult dermatologist for therapy',
            'Maintain healthy diet — Vitamin B12 & D3 help',
        ]
    },
    'melanoma': {
        'name': '🚨 MELANOMA',
        'desc': '⚠️ Possible skin cancer detected!',
        'tips': [
            'SEEK IMMEDIATE MEDICAL ATTENTION',
            'Visit a dermatologist or oncologist TODAY',
            'Do NOT delay',
            'Avoid sun exposure',
        ]
    },
    'normal_skin': {
        'name': '✅ Normal Skin',
        'desc': 'No skin condition detected',
        'tips': [
            'Continue daily skincare routine',
            'Apply sunscreen SPF 30+ daily',
            'Stay hydrated',
            'Do monthly self checks',
        ]
    }
}

# ── YOLO MODEL LOADER ────────────────────────────────────────────────────────
model = None

def load_yolo_model():
    global model
    try:
        from ultralytics import YOLO
        model_path = 'medicuslabs_best.pt'
        if os.path.exists(model_path):
            model = YOLO(model_path)
            print("✅ Model loaded!")
        else:
            print("⚠️ Model file not found")
    except Exception as e:
        print(f"❌ Model load error: {e}")

# ── ISIC API INTEGRATION ─────────────────────────────────────────────────────
def get_isic_similar_images(disease_name: str):
    """Get similar images from ISIC database"""
    try:
        isic_diagnosis_map = {
            'acne': 'Acne',
            'eczema': 'Dermatitis',
            'psoriasis': 'Psoriasis',
            'ringworm': 'Tinea',
            'vitiligo': 'Vitiligo',
            'melanoma': 'Melanoma',
            'normal_skin': 'Nevus'
        }
        
        diagnosis = isic_diagnosis_map.get(disease_name, disease_name)
        
        # Query ISIC API
        params = {
            'diagnosis': diagnosis,
            'limit': 3,
            'offset': 0
        }
        
        response = requests.get('https://api.isic-archive.com/api/v2/images/', params=params, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            return [
                {
                    'id': img.get('id'),
                    'diagnosis': img.get('metadata', {}).get('clinical', {}).get('diagnosis', '')
                }
                for img in data.get('results', [])[:3]
            ]
    except Exception as e:
        print(f"ISIC API error: {e}")
    
    return []

# ── PREDICTION FUNCTION ──────────────────────────────────────────────────────
def predict_disease_image(image_bytes: bytes):
    """Predict disease from image bytes"""
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

        if hasattr(result, 'probs') and result.probs is not None:
            class_id = result.probs.top1
            confidence = float(result.probs.top1conf)
            class_names = result.names
            predicted_class = class_names[class_id].lower()
            
            predictions = {}
            for idx, prob in enumerate(result.probs.data):
                predictions[class_names[idx]] = float(prob)
            
            return predicted_class, confidence, predictions

    except Exception as e:
        print(f"Prediction error: {e}")

    return None, 0, {}

# ── EMAIL REPORT SENDER ──────────────────────────────────────────────────────
def send_email_report(email: str, report: Report):
    """Send analysis report via email"""
    try:
        disease_info = DISEASE_INFO.get(report.disease, DISEASE_INFO['normal_skin'])
        
        # Create HTML email
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px; }}
                h1 {{ color: #2c3e50; text-align: center; }}
                h2 {{ color: #e74c3c; }}
                .info {{ background: #ecf0f1; padding: 15px; border-radius: 5px; margin: 15px 0; }}
                .tips {{ background: #d5f4e6; padding: 15px; border-radius: 5px; margin: 15px 0; }}
                .urgent {{ background: #fadbd8; padding: 15px; border-radius: 5px; }}
                .footer {{ font-size: 12px; color: #7f8c8d; text-align: center; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🏥 MedicusLabs AI Report</h1>
                <hr>
                
                <h2>{disease_info['name']}</h2>
                
                <div class="info">
                    <p><strong>Diagnosis:</strong> {disease_info['desc']}</p>
                    <p><strong>AI Confidence:</strong> {report.confidence:.1%}</p>
                    <p><strong>Analysis Date:</strong> {report.created_at.strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
                
                <h3>💊 Recommendations:</h3>
                <div class="tips">
                    <ul>
        """
        
        for tip in disease_info['tips']:
            html_body += f"<li>{tip}</li>"
        
        html_body += """
                    </ul>
                </div>
                
                <div class="footer">
                    <p>⚕️ <strong>Medical Disclaimer:</strong> This report is for educational purposes only.</p>
                    <p>Always consult a qualified healthcare professional.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        msg = Message(
            subject=f'🏥 MedicusLabs Report: {disease_info["name"]}',
            recipients=[email],
            html=html_body
        )
        
        mail.send(msg)
        report.sent_at = datetime.utcnow()
        report.status = 'sent'
        db.session.commit()
        print(f"✅ Report sent to {email}")
        return True
    except Exception as e:
        print(f"Email error: {e}")
        return False

# ── ROUTES ───────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        name = request.form.get('name')

        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'Email already registered'}), 400

        user = User(email=email, name=name)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        return jsonify({'message': 'Registration successful! Please login.'}), 201

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            return jsonify({'error': 'Invalid credentials'}), 401

    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    user_reports = Report.query.filter_by(user_id=current_user.id).order_by(Report.created_at.desc()).all()
    return render_template('dashboard.html', reports=user_reports)

@app.route('/upload', methods=['POST'])
@login_required
def upload_image():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if not file.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
        return jsonify({'error': 'Invalid file format'}), 400

    try:
        # Save file
        filename = secure_filename(f"{current_user.id}_{datetime.utcnow().timestamp()}_{file.filename}")
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Read image
        with open(filepath, 'rb') as f:
            image_bytes = f.read()

        # Predict disease
        disease, confidence, predictions = predict_disease_image(image_bytes)

        if disease is None:
            return jsonify({'error': 'Could not analyze image'}), 400

        # Get ISIC matches
        isic_matches = get_isic_similar_images(disease)

        # Create report
        report = Report(
            user_id=current_user.id,
            disease=disease,
            confidence=confidence,
            image_path=filepath,
            analysis_data={
                'predictions': predictions,
                'isic_matches': isic_matches
            },
            status='pending'
        )
        db.session.add(report)
        db.session.commit()

        # Schedule email sending after 10 minutes
        timer = threading.Timer(600, send_email_report, args=[current_user.email, report])
        timer.daemon = True
        timer.start()

        return jsonify({
            'id': report.id,
            'disease': disease,
            'confidence': confidence,
            'message': f'Report will be emailed in 10 minutes!'
        }), 201

    except Exception as e:
        print(f"Upload error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/report/<int:report_id>')
@login_required
def view_report(report_id):
    report = Report.query.get_or_404(report_id)
    
    if report.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403

    report.status = 'viewed'
    db.session.commit()

    disease_info = DISEASE_INFO.get(report.disease, DISEASE_INFO['normal_skin'])

    return render_template('report.html', report=report, disease_info=disease_info)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# ── ERROR HANDLERS ───────────────────────────────────────────────────────────
@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({'error': 'Server error'}), 500

# ── INITIALIZATION ───────────────────────────────────────────────────────────
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    
    load_yolo_model()
    
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=5000, debug=debug_mode)
