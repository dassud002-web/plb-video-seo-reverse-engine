@echo off
setlocal
set "DEST="
set /p DEST=Enter an EMPTY folder path for recovery: 
if "%DEST%"=="" exit /b 1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0tools\plb-guardian\restore.ps1" -Destination "%DEST%"
pause
