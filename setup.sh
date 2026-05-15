#!/bin/bash

echo "🏥 MedicusLabs - Quick Setup Guide"
echo "===================================="
echo ""

# Check Python version
echo "✅ Checking Python version..."
python_version=$(python --version 2>&1 | awk '{print $2}')
echo "   Python $python_version found"
echo ""

# Create virtual environment
echo "✅ Creating virtual environment..."
python -m venv venv
source venv/Scripts/activate  # On Windows: venv\Scripts\activate
echo "   Virtual environment created"
echo ""

# Install dependencies
echo "✅ Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
echo "   Dependencies installed"
echo ""

# Create .env file
echo "✅ Creating .env file..."
if [ ! -f .env ]; then
    cp .env.template .env
    echo "   .env created from template"
    echo "   ⚠️  Edit .env with your API keys!"
else
    echo "   .env already exists"
fi
echo ""

# Create directories
echo "✅ Creating required directories..."
mkdir -p uploads
mkdir -p logs
echo "   Directories created"
echo ""

# Check model file
echo "✅ Checking model file..."
if [ -f medicuslabs_best.pt ]; then
    echo "   ✓ Model file found"
else
    echo "   ⚠️  Model file not found!"
    echo "   Download medicuslabs_best.pt and place in root directory"
fi
echo ""

echo "🚀 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env with your API keys"
echo "2. Run locally: python web_app.py"
echo "3. Or use Docker: docker-compose up"
echo ""
