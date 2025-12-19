@echo off
REM Quick start script for Streamlit UI on Windows
echo ========================================
echo Starting Knowledge Base UI
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Set local API URL if not set
if "%RAG_API_URL%"=="" (
    set RAG_API_URL=http://localhost:8080
    echo Using local API: %RAG_API_URL%
)

echo Starting Streamlit...
streamlit run app.py

pause


