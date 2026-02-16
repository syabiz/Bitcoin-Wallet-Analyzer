@echo off
REM Bitcoin Wallet Analyzer - Quick Launcher for Windows
REM Script for running applications on Windows

echo ============================================================
echo   Bitcoin Wallet Analyzer - Profesional Edition by Syabiz
echo ============================================================
echo.

REM Check Python installation
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [X] Python not found!
    echo     Download from: https://www.python.org/downloads/
    echo     Make sure the "Add Python to PATH" checkbox is checked during installation.
    pause
    exit /b 1
)

echo [OK] Python was discovered

REM Check tkinter
python -c "import tkinter" >nul 2>&1
if %errorlevel% neq 0 (
    echo [X] tkinter not found!
    echo     Reinstall Python with the tcl/tk checkbox enabled
    pause
    exit /b 1
)

echo [OK] tkinter is available

REM Check numpy (optional)
python -c "import numpy" >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] numpy available (advanced analysis active^)
) else (
    echo [!] numpy not found (optional^)
    echo     Install with: pip install numpy
)

echo.
echo [RUN] Running Bitcoin Wallet Analyzer...
echo.

REM Run the application
python main.pyw

if %errorlevel% neq 0 (
    echo.
    echo [X] Error running application!
    echo     Make sure the main.pyw file exists
    pause
    exit /b 1
)
