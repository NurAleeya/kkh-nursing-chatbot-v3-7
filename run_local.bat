@echo off
REM KKH Nursing Chatbot - Local Development Setup for Windows

echo 🏥 KKH Nursing Chatbot - Local Setup
echo ===================================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.11+ from https://python.org
    pause
    exit /b 1
)

echo ✅ Python found

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo 📋 Installing dependencies...
pip install -r requirements.txt

REM Run the application
echo 🚀 Starting KKH Nursing Chatbot...
echo.
echo The application will be available at: http://localhost:8501
echo Press Ctrl+C to stop the application
echo.
streamlit run app.py

pause
