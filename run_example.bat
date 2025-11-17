@echo off
REM Helper script to run the example evaluation on Windows

echo ==========================================
echo Candidate-Job Matching System - Example
echo ==========================================
echo.

REM Check if virtual environment exists
if not exist "venv\" if not exist ".venv\" (
    echo No virtual environment found. Creating one...
    python -m venv venv
    call venv\Scripts\activate.bat
    pip install -r requirements.txt
) else (
    if exist "venv\" (
        call venv\Scripts\activate.bat
    ) else (
        call .venv\Scripts\activate.bat
    )
)

REM Check if .env exists
if not exist ".env" (
    echo ERROR: .env file not found!
    echo Please copy env.example to .env and configure your API keys.
    exit /b 1
)

REM Run the example
echo Running example evaluation...
echo.
python notebooks\example_evaluation.py

echo.
echo ==========================================
echo Example complete!
echo ==========================================

