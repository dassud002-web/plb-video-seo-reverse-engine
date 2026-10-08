@echo off
setlocal
cd /d "%~dp0"

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0tools\plb-guardian\install.ps1"
set "EXITCODE=%ERRORLEVEL%"

echo.
if not "%EXITCODE%"=="0" (
    echo Guardian installation FAILED. Exit code: %EXITCODE%
    echo.
    pause
    exit /b %EXITCODE%
)

echo Guardian installation completed successfully.
echo.
pause
