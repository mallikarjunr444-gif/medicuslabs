# 🏥 MedicusLabs - AI-Powered Skin Disease Detection

**Professional-grade AI system for skin disease detection with Telegram bot, web dashboard, and ISIC database integration.**

![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg)

---

## 📋 Overview

MedicusLabs is an advanced AI system that detects 7 skin conditions using:
- **YOLOv8 Deep Learning** - Real-time detection
- **ISIC Database** - 500,000+ medical images for validation
- **Hugging Face Models** - Enhanced predictions
- **Email Reports** - Automated delivery in 10 minutes

### Detects:
- 🔴 Acne
- 🔴 Eczema
- 🔴 Psoriasis  
- ⚠️ Ringworm (Tinea)
- ⚪ Vitiligo
- 🚨 Melanoma (URGENT)
- ✅ Normal Skin

---

## 🚀 Quick Start

### Option 1: Docker (Recommended)
```bash
# Clone repository
git clone https://github.com/yourusername/medicuslabs.git
cd medicuslabs

# Setup environment
cp .env.template .env
# Edit .env with your API keys

# Run with Docker
docker-compose up
# Visit http://localhost:5000
```

### Option 2: Local Installation (Windows)
```bash
# Run setup script
.\setup.bat

# Or manually:
python -m venv venv
venv\Scripts\activate.bat
pip install -r requirements.txt
python web_app.py
```

### Option 3: Local Installation (Linux/Mac)
```bash
# Run setup script
bash setup.sh

# Or manually:
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python web_app.py
```

---

## 📱 Features

### 🤖 Telegram Bot
- Real-time image analysis
- ISIC database matching
- Email report delivery
- Detailed medical recommendations
- Multi-language support (coming soon)

**Usage:**
```
/start - Welcome message
/help - Instructions
/about - About MedicusLabs
📸 Send photo to analyze
```

### 🌐 Web Dashboard
- Email authentication
- Drag-drop image upload
- Real-time AI analysis
- Email report delivery
- Report history & tracking
- Beautiful responsive UI

### 📊 ISIC Integration
- Matches against 500,000+ medical images
- Real diagnosis validation
- Similar cases reference
- Confidence scoring

### 📧 Email Reports
- Automated 10-minute delivery
- Professional formatting
- Detailed recommendations
- Medical disclaimer
- One-click report viewing

---

## 🔧 Configuration

### Environment Variables
Create `.env` file:
```env
# Telegram
TELEGRAM_BOT_TOKEN=your_token_here

# Email
EMAIL_SENDER=your_email@gmail.com
EMAIL_PASSWORD=app_specific_password

# Hugging Face
HF_API_TOKEN=hf_your_token

# Flask
SECRET_KEY=your_secret_key
FLASK_ENV=production

# Database (optional for local SQLite)
DATABASE_URL=postgresql://user:pass@host/db
```

### Getting API Tokens

#### 1. Telegram Bot Token
- Chat with [@BotFather](https://t.me/botfather) on Telegram
- `/newbot` → Follow instructions
- Copy token to `TELEGRAM_BOT_TOKEN`

#### 2. Gmail App Password
- Enable 2FA on Gmail
- Go to https://myaccount.google.com/apppasswords
- Create app password
- Copy to `EMAIL_PASSWORD` (NOT your Gmail password!)

#### 3. Hugging Face Token
- Go to https://huggingface.co/settings/tokens
- Create new access token
- Copy to `HF_API_TOKEN`

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│      MedicusLabs System (v2.0)          │
├─────────────────────────────────────────┤
│                                         │
│  ┌──────────────┐    ┌──────────────┐  │
│  │ Telegram Bot │    │ Web Dashboard│  │
│  │  (telegram_  │    │  (Flask app) │  │
│  │  bot_v2.py)  │    │   web_app.py)│  │
│  └──────┬───────┘    └───────┬──────┘  │
│         │                    │         │
│         └────────┬───────────┘         │
│                  │                     │
│         ┌────────▼────────┐           │
│         │  YOLOv8 Model   │           │
│         │ (medicuslabs_   │           │
│         │   best.pt)      │           │
│         └────────┬────────┘           │
│                  │                    │
│    ┌─────────────┼─────────────┐     │
│    │             │             │     │
│  ┌─▼──┐  ┌──────▼─────┐  ┌───▼──┐  │
│  │ISIC │  │Hugging Face│  │Email │  │
│  │API  │  │   Models   │  │SMTP  │  │
│  └────┘  └────────────┘  └──────┘  │
│                                     │
│  ┌──────────────────────────────┐  │
│  │  PostgreSQL Database         │  │
│  │  (Users, Reports, History)   │  │
│  └──────────────────────────────┘  │
│                                     │
└─────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
medicuslabs/
├── web_app.py                 # Flask web application
├── telegram_bot_v2.py         # Advanced Telegram bot
├── telegram_bot.py            # Legacy bot (v1)
├── requirements.txt           # Python dependencies
├── Procfile.txt              # Railway deployment config
├── railpack.toml             # Railway system packages
├── Dockerfile                # Docker image definition
├── docker-compose.yml        # Docker compose config
├── setup.sh                  # Linux/Mac setup script
├── setup.bat                 # Windows setup script
├── .env.template             # Environment variables template
├── medicuslabs_best.pt       # YOLOv8 model (download separately)
├── SETUP_GUIDE.md            # Detailed setup guide
├── README.md                 # This file
├── templates/
│   ├── login.html            # User login page
│   ├── register.html         # User registration page
│   ├── dashboard.html        # Image upload dashboard
│   └── report.html           # Analysis report viewer
├── uploads/                  # User image uploads
└── logs/                     # Application logs
```

---

## 🚢 Deployment

### Option 1: Railway (Free with GitHub Student Pack)
```bash
# 1. Push to GitHub
git add .
git commit -m "Deploy MedicusLabs"
git push origin main

# 2. Connect to Railway
# - Go to railway.app
# - Connect GitHub repo
# - Add environment variables
# - Auto-deploy

# 3. Access your app
https://your-project.railway.app
```

### Option 2: Heroku
```bash
# 1. Install Heroku CLI
# 2. Create app
heroku create medicuslabs-app

# 3. Add buildpacks (fix OpenCV issue)
heroku buildpacks:add --index 1 heroku-community/apt

# 4. Deploy
git push heroku main

# 5. Open app
heroku open
```

### Option 3: AWS/Azure/GCP
- Use Docker image for easy deployment
- Dockerfile included in repository
- Follow cloud provider's container deployment guide

---

## 🧪 Testing

### Test Telegram Bot
```bash
export TELEGRAM_BOT_TOKEN="your_token"
python telegram_bot_v2.py
# Send /start to your bot
```

### Test Web App
```bash
export FLASK_ENV=development
python web_app.py
# Visit http://localhost:5000
# Register and upload test image
```

### Test Email Delivery
```bash
# Upload image on web dashboard
# Check email after 10 minutes
# Verify formatting and content
```

### Test ISIC Integration
```python
from telegram_bot_v2 import get_isic_similar_images
import asyncio

result = asyncio.run(get_isic_similar_images('melanoma'))
print(result)  # Should return similar melanoma cases
```

---

## 🐛 Troubleshooting

### Bot Not Responding
```
✅ Fix: Check TELEGRAM_BOT_TOKEN is correct and bot is running
   Check logs: tail -f logs/bot.log
   Verify token: python -c "import telegram; telegram.Bot(token='YOUR_TOKEN').get_me()"
```

### Model Not Loading
```
✅ Fix 1: Download medicuslabs_best.pt and place in root directory
   Fix 2: Fallback to Hugging Face - set HF_API_TOKEN
   Check: python -c "from ultralytics import YOLO; YOLO('medicuslabs_best.pt')"
```

### Email Not Sending
```
✅ Fix 1: Verify EMAIL_PASSWORD is app-specific (not Gmail password)
   Fix 2: Enable "Less secure app access" or use app password
   Fix 3: Check email configuration: echo $EMAIL_SENDER
   Debug: python -c "import smtplib; smtplib.SMTP_SSL('smtp.gmail.com', 465).ehlo()"
```

### ISIC API Timeout
```
✅ Fix: Add timeout handling and retries
   Check: curl https://api.isic-archive.com/api/v2/images/?limit=1
   Rate limit: Add delays between requests
```

### Database Connection Error
```
✅ Fix: Check DATABASE_URL is valid and PostgreSQL is running
   For local: DATABASE_URL=sqlite:///medicuslabs.db
   For prod: DATABASE_URL=postgresql://user:pass@host:5432/db
```

---

## 🔐 Security

- ✅ Password hashing with werkzeug
- ✅ CSRF protection
- ✅ SQL injection prevention (SQLAlchemy ORM)
- ✅ File upload validation
- ✅ HTTPS enforcement (production)
- ✅ Rate limiting (recommended)
- ✅ Email verification (optional)

### Recommended Production Settings:
```python
# Enable HTTPS
FLASK_ENV = 'production'
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True

# Add rate limiting
from flask_limiter import Limiter
limiter = Limiter(app, key_func=lambda: current_user.id)
```

---

## 📚 API Documentation

### Telegram Bot Endpoints
```
GET /start          → Welcome message
GET /help           → Help instructions
GET /about          → About information
POST /photo         → Analyze skin image
POST /document      → Process document
```

### Web API Endpoints
```
POST   /register    → Create new account
POST   /login       → User authentication
GET    /dashboard   → View reports
POST   /upload      → Submit image
GET    /report/<id> → View detailed report
GET    /logout      → End session
```

### ISIC API
```
GET /api/v2/images/
    ?diagnosis=Melanoma
    &limit=5
    &offset=0

Returns:
{
  "results": [
    {
      "id": "ISIC_0024306",
      "metadata": {
        "clinical": {
          "diagnosis": "Melanoma",
          "image": "https://..."
        }
      }
    }
  ]
}
```

---

## 🤝 Contributing

We welcome contributions! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup
```bash
git clone https://github.com/yourusername/medicuslabs.git
cd medicuslabs
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

---

## 📝 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

---

## ⚠️ Medical Disclaimer

**IMPORTANT:** This system is designed for **educational and research purposes only**. It is **NOT** a substitute for professional medical advice, diagnosis, or treatment.

- Always consult a qualified healthcare professional for proper medical evaluation
- Do not rely solely on this AI system for medical decisions
- In case of medical emergency, seek immediate professional help
- The accuracy of predictions depends on image quality and model training

---

## 👥 Team

- **Mallikarjun R** - AI & Machine Learning
- **Mohammad Adil** - Backend Development
- **Mallanagowda M** - DevOps & Deployment
- **Nigam Patel** - QA & Testing

**Institution:** DSATM, Bengaluru

---

## 📞 Support & Contact

- **GitHub Issues:** [Report bugs here](https://github.com/yourusername/medicuslabs/issues)
- **Email:** medicuslabs@example.com
- **Telegram:** [@MedicusLabsBot](https://t.me/medicuslabs)

---

## 🔗 Useful Links

- [ISIC Archive](https://www.isic-archive.com/)
- [Hugging Face](https://huggingface.co/)
- [Ultralytics YOLOv8](https://docs.ultralytics.com/)
- [Telegram Bot API](https://core.telegram.org/bots/api)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Railway Platform](https://railway.app/)

---

## 📊 Performance Metrics

| Metric | Value |
|--------|-------|
| Model Accuracy | 85%+ |
| Inference Time | <3 seconds |
| Email Delivery | 10 minutes |
| Database Query | <100ms |
| Uptime Target | 99.5% |
| Max Concurrent Users | 100+ |

---

**Last Updated:** May 14, 2026  
**Version:** 2.0.0  
**Status:** ✅ Production Ready

---

*Making AI-powered healthcare accessible to everyone* 🏥✨
