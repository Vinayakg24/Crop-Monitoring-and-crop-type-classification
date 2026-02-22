#!/bin/bash

echo "========================================"
echo "  Crop Classification App Launcher"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.8 or higher"
    exit 1
fi

echo "[1/4] Checking Python installation..."
python3 --version
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "[2/4] Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to create virtual environment"
        exit 1
    fi
    echo "Virtual environment created successfully!"
else
    echo "[2/4] Virtual environment already exists"
fi
echo ""

# Activate virtual environment
echo "[3/4] Activating virtual environment..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to activate virtual environment"
    exit 1
fi
echo ""

# Install/update requirements
echo "[4/4] Installing dependencies..."
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies"
    exit 1
fi
echo "Dependencies installed successfully!"
echo ""

# Check Earth Engine authentication
echo "========================================"
echo "  Checking Earth Engine Authentication"
echo "========================================"
python3 -c "import ee; ee.Initialize()" 2>/dev/null
if [ $? -ne 0 ]; then
    echo ""
    echo "WARNING: Earth Engine is not authenticated"
    echo "Please authenticate using: earthengine authenticate"
    echo ""
    read -p "Would you like to authenticate now? (y/n) " auth_choice
    if [ "$auth_choice" = "y" ] || [ "$auth_choice" = "Y" ]; then
        earthengine authenticate
    fi
    echo ""
fi

# Launch Streamlit app
echo "========================================"
echo "  Starting Crop Classification App"
echo "========================================"
echo ""
echo "The app will open in your default browser"
echo "Press Ctrl+C to stop the server"
echo ""
streamlit run crop_classification_app.py

# Deactivate on exit
deactivate
