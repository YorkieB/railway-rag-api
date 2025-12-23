@echo off
REM Windows batch script to run companion-api locally

echo Starting Real-Time AI Companion API...
echo.

REM Check if .env exists
if not exist .env (
    echo ERROR: .env file not found!
    echo Please copy .env.example to .env and add your API keys.
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
    echo Installing dependencies...
    call venv\Scripts\activate.bat
    echo Installing pipwin for PyAudio on Windows...
    pip install pipwin
    echo Installing PyAudio via pipwin (pre-built wheels)...
    pipwin install pyaudio
    echo Installing other dependencies...
    pip install -r requirements.txt
)

REM Activate virtual environment and run
echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Starting server on http://localhost:8080
echo Press Ctrl+C to stop
echo.

uvicorn main:app --host 0.0.0.0 --port 8080 --reload

pause

