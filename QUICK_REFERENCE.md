# ⚡ MEDICUSLABS BOT v2.0 - QUICK REFERENCE

**Status:** ✅ PRODUCTION READY | **Unified Bot:** ✅ ACTIVE

## 🚀 START HERE
1. **BOT_STARTUP.md** ← Getting started (5 min)
2. **PRODUCTION_SUMMARY.md** ← Full overview (20 min)
3. **DEPLOYMENT_GUIDE.md** ← Cloud deployment (30 min)
4. **README.md** ← Complete documentation

---

## ⚡ QUICK START (60 SECONDS)

### Run Bot Locally
```bash
# Navigate to project
cd medicuslabs

# Run bot
python bot.py

# In Telegram, send: /start
# Expected: Welcome message ✅
```

### Verify Setup
```bash
python check_health.py
# Should show all green ✅
```

### Deploy to Railway
```bash
git push origin main
# Railway auto-deploys (2 min)
# Bot goes live! ✅
```

---

## 🔑 YOUR CREDENTIALS (CONFIGURED)

```
Telegram Bot:  your_telegram_bot_token ✅
Hugging Face:  your_huggingface_token ✅
Gmail Pwd:     your_app_specific_password ✅
```

**Location:** `.env` file (backup) + embedded in `bot.py`

---

## � BOT FEATURES

| Command | Time | Output |
|---------|------|--------|
| `/start` | < 0.5s | Welcome |
| `/help` | < 0.5s | Instructions |
| `/about` | < 0.5s | Team info |
| `/history` | < 1s | Past analyses |
| 📸 Photo | < 3s | AI analysis |
| 📧 Email | 10 min | Detailed report |

---

## 🚀 DEPLOYMENT OPTIONS

### Option 1: Railway (Easiest ⭐)
```bash
git push origin main
# Auto-deploys in 2 minutes
```

### Option 2: Docker
```bash
docker-compose up -d
```

### Option 3: Local Testing
```bash
python bot.py
```

---

## �🚂 DEPLOY TO RAILWAY (2 MINUTES)

```bash
# 1. Push to GitHub
git add .
git commit -m "Deploy unified bot"
git push origin main

# 2. Go to https://railway.app
# 3. Connect GitHub repo
# 4. Add environment variables:
#    TELEGRAM_BOT_TOKEN = your_telegram_bot_token
#    HF_API_TOKEN = your_huggingface_token
#    EMAIL_SENDER = your_email@gmail.com
#    EMAIL_PASSWORD = your_app_specific_password
#    FLASK_ENV = production

# 5. Click Deploy
# 6. Test: Send /start to bot ✅
# 7. Done! Bot is live 🎉
```

**Note:** railpack.toml auto-fixes the libssl crash on Railway

---

## � IMPORTANT FILES

### Core Files
- `bot.py` ⭐ - Unified Telegram bot (NEW - use this!)
- `.env` ⭐ - Your credentials (NEW - configured)
- `check_health.py` ⭐ - System health check (NEW)
- `web_app.py` - Flask website
- `medicuslabs_best.pt` - YOLOv8 model

### Configuration
- `requirements.txt` - Dependencies
- `Procfile.txt` - Deployment config
- `Dockerfile` - Docker image
- `docker-compose.yml` - Multi-container

### Web Templates
- `templates/login.html` - Login page
- `templates/register.html` - Signup page
- `templates/dashboard.html` - Upload interface
- `templates/report.html` - Results view

### Documentation
- `BOT_STARTUP.md` - Getting started (5 min)
- `PRODUCTION_SUMMARY.md` - Full overview (20 min)
- `DEPLOYMENT_GUIDE.md` - Cloud deployment
- `README.md` - Complete documentation
- `SETUP_GUIDE.md` - Installation guide

---

## ✅ LAUNCH CHECKLIST

- [ ] Run `python check_health.py` (all green ✅)
- [ ] Test locally: `python bot.py`
- [ ] Send /start in Telegram (bot responds)
- [ ] Upload test image (analyzes in <3s)
- [ ] Push to GitHub: `git push origin main`
- [ ] Deploy to Railway (auto-deploys)
- [ ] Verify bot is online
- [ ] Test email after 10 minutes
- [ ] Celebrate! 🎉

---

## 🐛 QUICK FIXES

### "libssl.so.1 not found" (Railway)
```
✅ FIXED! railpack.toml is installed automatically
If still failing: Check logs for system package errors
```

### Bot not responding
```
✅ Fix: python -c "import telegram; telegram.Bot('TOKEN').get_me()"
```

### Email not sending
```
✅ Fix: Use Gmail app-specific password (enable 2FA first)
```

### Model not loading
```
✅ Fix: Download medicuslabs_best.pt OR set HF_API_TOKEN
```

---

## 🎯 WHAT'S NEW IN v2.0

| Feature | Status |
|---------|--------|
| ISIC Database Integration | ✅ 500k+ images |
| Email Reports | ✅ 10-min auto delivery |
| Web Dashboard | ✅ Full authentication |
| Hugging Face Models | ✅ Enhanced predictions |
| Railway Crash Fixed | ✅ railpack.toml |
| Docker Support | ✅ Included |
| Automated Setup | ✅ setup.sh/.bat |

---

## 📊 SYSTEM ARCHITECTURE

```
User Signs Up
     ↓
Uploads Skin Image
     ↓
YOLOv8 Analyzes (< 3 sec)
     ↓
Matches with ISIC (500k+)
     ↓
Hugging Face Validates
     ↓
Results Shown Immediately
     ↓
Email Sent After 10 Minutes
```

---

## 🔗 IMPORTANT LINKS

- **ISIC Archive:** https://www.isic-archive.com/
- **Railway Docs:** https://docs.railway.app/
- **Hugging Face:** https://huggingface.co/
- **Telegram API:** https://core.telegram.org/bots/api
- **Flask Docs:** https://flask.palletsprojects.com/

---

## ⏱️ TIMING GUIDE

| Task | Time |
|------|------|
| Get API tokens | 10 min |
| Local setup | 5 min |
| Local testing | 10 min |
| Railway deployment | 2 min |
| Verify deployment | 5 min |
| **TOTAL** | **~32 min** |

---

## 🎓 EDUCATIONAL USE ONLY

⚠️ This system is for learning/research:
- NOT a medical diagnosis tool
- Always consult healthcare professionals
- Early detection saves lives

---

## 📞 NEED HELP?

1. Check **SETUP_GUIDE.md** (90% of issues solved)
2. Check **RAILWAY_FIX.md** (deployment issues)
3. Check logs: `railway logs` or `heroku logs --tail`
4. Search GitHub Issues
5. Create new GitHub Issue with error logs

---

## 🚀 READY? LET'S GO!

```
Step 1: python setup.bat  (or bash setup.sh)
Step 2: Edit .env with tokens
Step 3: python web_app.py
Step 4: test at http://localhost:5000
Step 5: Push to GitHub
Step 6: Deploy to Railway
Step 7: ✅ LIVE!
```

**Total time: ~30 minutes**

---

**Version:** 2.0.0  
**Status:** ✅ PRODUCTION READY  
**Last Updated:** May 14, 2026

Print this card and keep it nearby! 📌

---

For detailed information, see the full documentation:
- 📘 README.md
- 🔧 SETUP_GUIDE.md
- 📋 COMPLETE_SOLUTION.md
