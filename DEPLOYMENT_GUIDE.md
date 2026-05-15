# 🚀 DEPLOYMENT GUIDE - MEDICUSLABS

## ✅ BOT STATUS: PRODUCTION READY

Your unified bot (`bot.py`) is fully configured and ready for deployment!

```
✅ Credentials Embedded
✅ All Integrations Connected
✅ Error Handling Implemented
✅ Logging Configured
✅ Docker Support Ready
```

---

## 🎯 DEPLOYMENT OPTIONS

### 1️⃣ RAILWAY DEPLOYMENT (Recommended - FREE ⭐)

**Why Railway?**
- ✅ Free tier with Railway Student Pack
- ✅ Auto-deploys on git push
- ✅ Supports background workers (bot)
- ✅ PostgreSQL database included
- ✅ Email notifications
- ✅ Perfect for 24/7 bot hosting

**Steps:**

#### Step 1: Sign Up
```
1. Go to https://railway.app
2. Click "Start Project"
3. Connect GitHub account
4. Authorize Railway
```

#### Step 2: Create Project
```
1. Click "Deploy from GitHub repo"
2. Select your medicuslabs repository
3. Click "Deploy"
```

#### Step 3: Configure Environment
```
1. Go to Railway Dashboard
2. Click your project
3. Go to "Variables" tab
4. Add these variables:

   Variable Name              Value
   ──────────────────────────────────────────────
   TELEGRAM_BOT_TOKEN        your_telegram_bot_token
   HF_API_TOKEN              your_huggingface_token
   EMAIL_SENDER              your_email@gmail.com
   EMAIL_PASSWORD            your_app_specific_password
   SECRET_KEY                (generate random: openssl rand -hex 32)
   DATABASE_URL              (auto-populated by Railway)
   FLASK_ENV                 production
```

#### Step 4: Deploy
```
1. Railway auto-deploys on git push
2. Or click "Deploy" button manually
3. Wait 2-3 minutes for build
4. Check logs: railway logs
```

#### Step 5: Verify
```
1. Open Telegram
2. Send /start to @MedicusLabsBot
3. Bot should respond
4. Try uploading an image
5. Check email after 10 minutes
```

**Railway Logs:**
```bash
# Terminal command
railway logs --service bot

# Or via Dashboard
Railway → Project → Logs
```

**Monitor Bot:**
```
Dashboard → Metrics tab
- CPU usage
- Memory usage
- Request count
- Error logs
```

---

### 2️⃣ HEROKU DEPLOYMENT

**Why Heroku?**
- ✅ Easy-to-use CLI
- ✅ Supports background jobs
- ✅ Good documentation
- ✅ Free tier available

**Steps:**

#### Step 1: Install Heroku CLI
```bash
# Windows
choco install heroku-cli

# Mac
brew tap heroku/brew && brew install heroku

# Linux
curl https://cli-assets.heroku.com/install.sh | sh
```

#### Step 2: Login
```bash
heroku login
```

#### Step 3: Create App
```bash
heroku create medicuslabs-bot
```

#### Step 4: Add PostgreSQL
```bash
heroku addons:create heroku-postgresql:hobby-dev
```

#### Step 5: Set Environment Variables
```bash
heroku config:set TELEGRAM_BOT_TOKEN="your_telegram_bot_token"
heroku config:set HF_API_TOKEN="your_huggingface_token"
heroku config:set EMAIL_SENDER="your_email@gmail.com"
heroku config:set EMAIL_PASSWORD="your_app_specific_password"
heroku config:set SECRET_KEY="$(openssl rand -hex 32)"
heroku config:set FLASK_ENV="production"
```

#### Step 6: Deploy
```bash
git push heroku main
```

#### Step 7: Monitor
```bash
heroku logs --tail
heroku ps
```

---

### 3️⃣ DOCKER DEPLOYMENT

**Why Docker?**
- ✅ Works on any platform
- ✅ Reproducible environment
- ✅ Easy horizontal scaling
- ✅ Local testing before deploy

**Setup (Already Provided):**
- ✅ `Dockerfile` - Container image
- ✅ `docker-compose.yml` - Multi-container setup
- ✅ `railpack.toml` - Railway system packages

**Commands:**

#### Build Locally
```bash
# Build Docker image
docker build -t medicuslabs:latest .

# Or with compose
docker-compose build
```

#### Run Locally
```bash
# Start all services
docker-compose up

# Detached mode (background)
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f bot
```

#### Deploy to Docker Hub
```bash
# Login
docker login

# Tag image
docker tag medicuslabs:latest yourusername/medicuslabs:latest

# Push
docker push yourusername/medicuslabs:latest
```

#### AWS / Google Cloud / Azure
```bash
# Each cloud provider has Docker deployment options
# They auto-pull from Docker Hub or your registry
```

---

### 4️⃣ AWS DEPLOYMENT

**With EC2 + Docker:**

```bash
# 1. Launch EC2 instance (Ubuntu)
# 2. SSH into instance
ssh -i key.pem ec2-user@instance.com

# 3. Install Docker
sudo yum update -y
sudo yum install docker -y
sudo systemctl start docker

# 4. Clone repo
git clone https://github.com/yourusername/medicuslabs.git
cd medicuslabs

# 5. Create .env file
cat > .env << EOF
TELEGRAM_BOT_TOKEN=...
HF_API_TOKEN=...
EMAIL_SENDER=...
EMAIL_PASSWORD=...
EOF

# 6. Run with Docker Compose
docker-compose up -d

# 7. Verify
docker-compose logs -f bot
```

---

### 5️⃣ GOOGLE CLOUD DEPLOYMENT

**With Cloud Run:**

```bash
# 1. Install Google Cloud CLI
# https://cloud.google.com/sdk/docs/install

# 2. Initialize
gcloud init

# 3. Create project
gcloud projects create medicuslabs

# 4. Build for Cloud Run
gcloud builds submit --tag gcr.io/medicuslabs/bot

# 5. Deploy
gcloud run deploy medicuslabs-bot \
  --image gcr.io/medicuslabs/bot \
  --platform managed \
  --region us-central1 \
  --set-env-vars TELEGRAM_BOT_TOKEN="..." \
  --set-env-vars HF_API_TOKEN="..."

# 6. Monitor
gcloud logging read "resource.type=cloud_run_revision"
```

---

## 📋 PRE-DEPLOYMENT CHECKLIST

Before deploying, verify everything:

```
✅ BEFORE YOU DEPLOY:

[ ] Code
    [ ] All files committed to git
    [ ] No uncommitted changes
    [ ] bot.py includes your credentials
    [ ] requirements.txt has all packages
    
[ ] Configuration
    [ ] Telegram bot token valid
    [ ] Hugging Face token valid
    [ ] Email credentials correct
    [ ] SECRET_KEY set to random value
    
[ ] Testing
    [ ] Run: python bot.py (starts)
    [ ] Run: python check_health.py (all green)
    [ ] Send /start to bot (responds)
    [ ] Upload test image (analyzes)
    [ ] Wait 10 min (email arrives)
    
[ ] Documentation
    [ ] README.md updated with deployment links
    [ ] Environment variables documented
    [ ] Credentials stored securely
    
[ ] Security
    [ ] No hardcoded passwords in code
    [ ] No .env file committed to git
    [ ] .gitignore includes .env
    [ ] Credentials only in deployment config
```

---

## 🔍 VERIFICATION AFTER DEPLOYMENT

### 1. Bot Responds
```
✅ Send /start
✅ Receive welcome message
✅ Response time < 2 seconds
```

### 2. Photo Analysis Works
```
✅ Send skin image
✅ Receive analysis in < 3 seconds
✅ Disease name shown
✅ Confidence percentage shown
✅ ISIC database matches shown
```

### 3. Email Delivery
```
✅ Wait 10 minutes
✅ Email arrives in inbox
✅ Professional HTML format
✅ Contains diagnosis
✅ Contains recommendations
✅ Contains medical references
```

### 4. Logs are Clean
```
✅ No error messages
✅ No timeout warnings
✅ No authentication failures
✅ No crashes
```

**Check Logs:**
```bash
# Railway
railway logs

# Heroku
heroku logs --tail

# Docker
docker-compose logs -f

# AWS
# Check CloudWatch logs

# Google Cloud
gcloud logging read
```

---

## 🚨 COMMON DEPLOYMENT ISSUES

### Issue 1: Bot Not Responding
```
❌ Problem: Send /start, no response

Solution:
1. Check if deployment is running
2. Verify TELEGRAM_BOT_TOKEN is correct
3. Check logs for errors
4. Make sure bot.py is the entrypoint

Fix:
heroku logs --tail          # see errors
railway logs                 # see errors
docker-compose logs -f bot  # see errors
```

### Issue 2: Model File Not Found
```
❌ Error: medicuslabs_best.pt: No such file

Solution:
Bot automatically falls back to Hugging Face
Check HF_API_TOKEN is set correctly

Verify:
- Check logs for "Using Hugging Face"
- Image analysis should still work
- Might be slightly slower
```

### Issue 3: Email Not Sending
```
❌ Error: SMTPAuthenticationError

Solution:
1. Verify EMAIL_PASSWORD is app-specific password
2. NOT your main Gmail password
3. Check 2FA is enabled on Gmail
4. Regenerate app password

Generate New Gmail App Password:
1. Go to myaccount.google.com
2. Security → App passwords
3. Select Mail + Linux
4. Copy password
5. Update EMAIL_PASSWORD in config
```

### Issue 4: ISIC API Timeout
```
⚠️ Warning: ISIC API request timeout

Solution:
This is non-blocking - bot continues without ISIC
If frequent, check internet connection on deployment server
Check if https://api.isic-archive.com is accessible

Test:
curl https://api.isic-archive.com/api/v2/images
```

---

## 📊 MONITORING & ANALYTICS

### Key Metrics to Monitor
```
✅ Bot Response Time (should be < 3s)
✅ Error Rate (should be 0%)
✅ Daily Active Users
✅ Image Analyses Per Day
✅ Email Delivery Rate (should be 100%)
```

### Railway Monitoring
```
Dashboard → Metrics
- View CPU, Memory, Network
- See request count
- Monitor error rates
```

### Heroku Monitoring
```
heroku metrics
heroku ps

# Or dashboard
https://dashboard.heroku.com/apps/medicuslabs-bot
```

### Docker Monitoring
```
docker stats
docker logs -f container_name
```

---

## 🔐 SECURITY BEST PRACTICES

### ✅ DO:
```
✅ Store credentials in environment variables
✅ Use .env file locally (add to .gitignore)
✅ Use deployment platform's secrets manager
✅ Rotate credentials regularly
✅ Use HTTPS for all API calls
✅ Validate user input
✅ Log security events
✅ Monitor for suspicious activity
```

### ❌ DON'T:
```
❌ Commit credentials to git
❌ Share .env file publicly
❌ Use same password everywhere
❌ Log sensitive data
❌ Trust user input
❌ Leave debug mode on
❌ Use HTTP (always HTTPS)
```

---

## 🎯 FINAL DEPLOYMENT STEPS

### 1. Verify Code
```bash
cd /path/to/medicuslabs
git status               # nothing uncommitted
cat .gitignore          # includes .env, __pycache__, .venv
cat bot.py              # has your credentials
```

### 2. Run Local Test
```bash
python check_health.py
# Should show all ✅ PASS
```

### 3. Push to GitHub
```bash
git add .
git commit -m "Deploy production bot with credentials"
git push origin main
```

### 4. Deploy
```bash
# Option A: Railway
# (auto-deploys on push, just check logs)

# Option B: Heroku
heroku create medicuslabs-bot
# ... configure env variables ...
git push heroku main

# Option C: Docker Locally
docker-compose up -d
```

### 5. Monitor
```bash
# Check deployment
railway logs        # or heroku logs --tail

# Test bot
# Send /start to bot

# Wait 10 minutes
# Check email arrives
```

### 6. Celebrate 🎉
```
Your bot is now live!

Share it:
@MedicusLabsBot

Check:
https://medicuslabs.railway.app  (web dashboard)
```

---

## 📞 SUPPORT MATRIX

| Issue | Local | Railway | Heroku | Docker |
|-------|-------|---------|--------|--------|
| Model not loading | ✅ HF fallback | ✅ HF fallback | ✅ HF fallback | ✅ HF fallback |
| Email not sending | Check password | Check env vars | Check env vars | Check .env |
| Bot offline | Restart bot | Check logs | Check logs | docker restart |
| Database error | Check SQLite | Check PostgreSQL | Check PostgreSQL | Check DB service |

---

## ✨ YOU'RE READY TO DEPLOY!

```
Your MedicusLabs bot is production-ready!

Recommended: Start with Railway (easiest)

Next:
1. Go to https://railway.app
2. Connect GitHub
3. Deploy your repo
4. Add environment variables
5. Done! Bot is live! 🚀
```

---

**Questions?** Check:
- `README.md` - Full documentation
- `BOT_STARTUP.md` - Getting started
- `SETUP_GUIDE.md` - Installation guide
- `RAILWAY_FIX.md` - Railway specific issues

**Your bot is ready! 🎉**
