@echo off
echo Starting MoodMusic...
echo --------------------------------
echo DO NOT USE STREAMLIT.
echo This is a Flask application.
echo --------------------------------

REM Check if .venv exists
if not exist ".venv" (
    echo Virtual environment not found. Please run installation.
    pause
    exit /b
)

REM Install Flask if missing (quick check)
.venv\Scripts\pip install flask >nul 2>&1

REM Run the app
.venv\Scripts\python.exe app.py

pause
