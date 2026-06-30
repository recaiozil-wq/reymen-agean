@echo off
chcp 65001 >nul
title ReYMeN Desktop
cd /d "%~dp0"
echo ReYMeN Desktop baslatiliyor...
echo.
echo Komutlar: start, stop, restart, status, tray, autostart
echo.
if "%1"=="" (
    call venv\Scripts\python.bat -m reymen.desktop.launcher start
    echo.
    echo Web UI: http://localhost:5000
    echo.
    pause
) else (
    call venv\Scripts\python.bat -m reymen.desktop.launcher %1
)
