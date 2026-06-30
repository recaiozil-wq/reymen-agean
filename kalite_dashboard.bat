@echo off
chcp 65001 >nul
title ReYMeN Kalite Dashboard
cd /d "%~dp0"
echo ========================================
echo  ReYMeN Kalite & Analytics Dashboard
echo ========================================
echo.
echo  Web UI: http://localhost:5000/kalite
echo  API:    http://localhost:5000/api/kalite/metrikler
echo.
echo  Press Ctrl+C to stop
echo ========================================
echo.

call venv\Scripts\python -m uvicorn reymen.web_ui:app --host 0.0.0.0 --port 5000 --log-level info

pause
