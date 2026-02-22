@echo off
echo ========================================
echo   Crop Classification App Launcher
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher
    pause
    exit /b 1
)

echo [1/4] Checking Python installation...
python --version
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo [2/4] Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
    echo Virtual environment created successfully!
) else (
    echo [2/4] Virtual environment already exists
)
echo.

REM Activate virtual environment
echo [3/4] Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)
echo.

REM Install/update requirements
echo [4/4] Installing dependencies...
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo Dependencies installed successfully!
echo.

REM Check Earth Engine authentication
echo ========================================
echo   Checking Earth Engine Authentication
echo ========================================
python -c "import ee; ee.Initialize()" >nul 2>&1
if errorlevel 1 (
    echo.
    echo WARNING: Earth Engine is not authenticated
    echo Please authenticate using: earthengine authenticate
    echo.
    echo Would you like to authenticate now? (Y/N)
    set /p auth_choice=
    if /i "%auth_choice%"=="Y" (
        earthengine authenticate
    )
    echo.
)

REM Launch Streamlit app
echo ========================================
echo   Starting Crop Classification App
echo ========================================
echo.
echo The app will open in your default browser
echo Press Ctrl+C to stop the server
echo.
streamlit run crop_classification_app.py

REM Deactivate on exit
deactivate
pause
