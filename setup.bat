@echo off
echo 🏥 MedicusLabs - Quick Setup Guide (Windows)
echo ============================================
echo.

echo ✅ Checking Python version...
python --version
echo.

echo ✅ Creating virtual environment...
python -m venv venv
call venv\Scripts\activate.bat
echo    Virtual environment created
echo.

echo ✅ Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt
echo    Dependencies installed
echo.

echo ✅ Creating .env file...
if not exist .env (
    copy .env.template .env
    echo    .env created from template
    echo    ⚠️  Edit .env with your API keys!
) else (
    echo    .env already exists
)
echo.

echo ✅ Creating required directories...
if not exist uploads mkdir uploads
if not exist logs mkdir logs
echo    Directories created
echo.

echo ✅ Checking model file...
if exist medicuslabs_best.pt (
    echo    ✓ Model file found
) else (
    echo    ⚠️  Model file not found!
    echo    Download medicuslabs_best.pt and place in root directory
)
echo.

echo 🚀 Setup complete!
echo.
echo Next steps:
echo 1. Edit .env with your API keys
echo 2. Run locally: python web_app.py
echo 3. Or use Docker: docker-compose up
echo.
pause
