@echo off
REM Search App Setup Script for Windows
REM This script sets up the search app with ADK and A2A integration

echo 🚀 Setting up Search App with A2A Integration
echo ==============================================

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is required but not installed
    pause
    exit /b 1
)

echo ✅ Python found

REM Create virtual environment if it doesn't exist
if not exist ".venv" (
    echo 📦 Creating virtual environment...
    python -m venv .venv
    echo ✅ Virtual environment created
) else (
    echo ✅ Virtual environment already exists
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call .venv\Scripts\activate.bat

REM Upgrade pip
echo ⬆️  Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies
echo 📚 Installing dependencies...
pip install -r requirements.txt

REM Create .env file if it doesn't exist
if not exist "app\.env" (
    echo ⚙️  Creating .env file from template...
    copy app\env.example app\.env
    echo ✅ .env file created
    echo ⚠️  Please edit app\.env and add your API keys
) else (
    echo ✅ .env file already exists
)

REM Test the setup
echo 🧪 Testing setup...
python test_setup.py

echo.
echo 🎉 Setup completed successfully!
echo.
echo Next steps:
echo 1. Edit app\.env and add your Google API key
echo 2. Run: cd app ^&^& adk web
echo 3. Open http://localhost:8000 in your browser
echo.
echo For A2A integration:
echo 1. Install A2A SDK: pip install a2a-sdk
echo 2. Configure A2A settings in app\.env
echo 3. Start your A2A agent registry
echo.
echo Happy coding! 🚀
pause 