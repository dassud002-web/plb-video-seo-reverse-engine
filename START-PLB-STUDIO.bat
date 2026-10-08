@echo off
title PLB Creator Studio - Desktop Edition
color 0b
echo ======================================================================
echo   ⚡ PLB CREATOR STUDIO — DESKTOP EDITION
echo   Unified Story Universe Factory + Video SEO Reverse Engine
echo ======================================================================
echo.
echo Starting application engines and launching native desktop window...
echo.

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH.
    echo Please install Python 3.10+ and add it to your system PATH.
    pause
    exit /b 1
)

python desktop_app.py
if %errorlevel% neq 0 (
    echo.
    echo Application exited with code %errorlevel%.
    pause
)
