#!/usr/bin/env python3
"""
🏥 MedicusLabs - System Health Check
Verify all integrations and configurations are working
"""

import os
import sys
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def check_python_version():
    """Check Python version"""
    version = sys.version_info
    logger.info(f"✅ Python Version: {version.major}.{version.minor}.{version.micro}")
    return True

def check_env_variables():
    """Check all required environment variables"""
    logger.info("\n📋 Checking Environment Variables...")
    
    required = {
        'TELEGRAM_BOT_TOKEN': 'Telegram Bot Token',
        'HF_API_TOKEN': 'Hugging Face Token',
        'EMAIL_SENDER': 'Email Sender',
        'EMAIL_PASSWORD': 'Email Password'
    }
    
    all_present = True
    for var, name in required.items():
        value = os.environ.get(var)
        if value:
            masked = value[:10] + '***' if len(value) > 10 else '***'
            logger.info(f"  ✅ {name}: {masked}")
        else:
            logger.warning(f"  ❌ {name}: NOT SET")
            all_present = False
    
    return all_present

def check_dependencies():
    """Check if required packages are installed"""
    logger.info("\n📦 Checking Python Dependencies...")
    
    packages = {
        'telegram': 'Telegram Bot Library',
        'cv2': 'OpenCV',
        'numpy': 'NumPy',
        'PIL': 'Pillow',
        'ultralytics': 'YOLOv8',
        'aiohttp': 'Async HTTP',
        'flask': 'Flask Web',
        'sqlalchemy': 'SQLAlchemy ORM'
    }
    
    all_installed = True
    for package, name in packages.items():
        try:
            __import__(package)
            logger.info(f"  ✅ {name}")
        except ImportError:
            logger.warning(f"  ❌ {name}: NOT INSTALLED")
            all_installed = False
    
    return all_installed

def check_model_file():
    """Check if YOLOv8 model exists"""
    logger.info("\n🤖 Checking AI Model...")
    
    model_path = 'medicuslabs_best.pt'
    if os.path.exists(model_path):
        size_mb = os.path.getsize(model_path) / (1024 * 1024)
        logger.info(f"  ✅ YOLOv8 Model: {size_mb:.1f} MB")
        return True
    else:
        logger.warning(f"  ⚠️  Model file not found: {model_path}")
        logger.info(f"     Hugging Face will be used as fallback")
        return False

def check_directories():
    """Check if required directories exist"""
    logger.info("\n📁 Checking Directories...")
    
    dirs = {
        'templates': 'Web Templates',
        'uploads': 'Image Uploads',
        'logs': 'Logs'
    }
    
    for dirname, name in dirs.items():
        if os.path.isdir(dirname):
            logger.info(f"  ✅ {name}: {dirname}/")
        else:
            logger.info(f"  📝 Creating {name}: {dirname}/")
            os.makedirs(dirname, exist_ok=True)
    
    return True

def check_telegram_token():
    """Verify Telegram bot token format"""
    logger.info("\n🤖 Checking Telegram Bot Token...")
    
    token = os.environ.get('TELEGRAM_BOT_TOKEN')
    if token and ':' in token:
        parts = token.split(':')
        if len(parts) == 2 and parts[0].isdigit():
            logger.info(f"  ✅ Token format: VALID")
            return True
    
    logger.warning(f"  ❌ Token format: INVALID")
    return False

def check_email_config():
    """Check email configuration"""
    logger.info("\n📧 Checking Email Configuration...")
    
    email = os.environ.get('EMAIL_SENDER')
    password = os.environ.get('EMAIL_PASSWORD')
    
    if email and '@' in email:
        logger.info(f"  ✅ Email: {email}")
    else:
        logger.warning(f"  ❌ Email: INVALID")
        return False
    
    if password:
        logger.info(f"  ✅ App Password: {password[:5]}***")
    else:
        logger.warning(f"  ❌ App Password: NOT SET")
        return False
    
    return True

def check_hf_token():
    """Check Hugging Face token"""
    logger.info("\n🤗 Checking Hugging Face Token...")
    
    token = os.environ.get('HF_API_TOKEN')
    if token and token.startswith('hf_'):
        logger.info(f"  ✅ Token format: VALID")
        return True
    
    logger.warning(f"  ❌ Token format: INVALID")
    return False

def check_bot_file():
    """Check if bot.py exists"""
    logger.info("\n🚀 Checking Bot Files...")
    
    files = {
        'bot.py': 'Unified Bot',
        'web_app.py': 'Web Dashboard',
        'requirements.txt': 'Dependencies',
        '.env': 'Configuration'
    }
    
    all_exist = True
    for filename, name in files.items():
        if os.path.isfile(filename):
            logger.info(f"  ✅ {name}: {filename}")
        else:
            logger.warning(f"  ❌ {name}: {filename} NOT FOUND")
            all_exist = False
    
    return all_exist

def main():
    """Run all health checks"""
    logger.info("\n" + "="*60)
    logger.info("🏥 MEDICUSLABS - SYSTEM HEALTH CHECK")
    logger.info("="*60)
    
    checks = [
        ("Python Version", check_python_version),
        ("Environment Variables", check_env_variables),
        ("Python Dependencies", check_dependencies),
        ("AI Model File", check_model_file),
        ("Directories", check_directories),
        ("Telegram Token", check_telegram_token),
        ("Email Config", check_email_config),
        ("Hugging Face Token", check_hf_token),
        ("Bot Files", check_bot_file),
    ]
    
    results = []
    for check_name, check_func in checks:
        try:
            result = check_func()
            results.append((check_name, result))
        except Exception as e:
            logger.error(f"❌ {check_name}: ERROR - {e}")
            results.append((check_name, False))
    
    # Summary
    logger.info("\n" + "="*60)
    logger.info("📊 HEALTH CHECK SUMMARY")
    logger.info("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for check_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{status} - {check_name}")
    
    logger.info("="*60)
    logger.info(f"Result: {passed}/{total} checks passed")
    
    if passed == total:
        logger.info("🟢 Status: READY TO RUN 🚀")
        logger.info("\nNext steps:")
        logger.info("1. python bot.py          (start bot)")
        logger.info("2. python web_app.py      (start website)")
        logger.info("3. Send /start to your bot on Telegram")
        return 0
    else:
        logger.warning("🟡 Status: SOME ISSUES FOUND")
        logger.info("\nFix issues and try again")
        return 1

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
