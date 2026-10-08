@echo off
title Build PLB Creator Studio Standalone Executable
color 0a
echo ======================================================================
echo   🛠️ BUILD PLB CREATOR STUDIO STANDALONE EXECUTABLE (.EXE)
echo ======================================================================
echo.

python scripts\build_standalone.py
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Build script exited with code %errorlevel%.
    pause
    exit /b %errorlevel%
)

echo.
echo Build completed successfully!
pause
