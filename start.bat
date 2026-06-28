@echo off
title ReYMeN Web UI
cd /d "%~dp0"
call venv\Scripts\activate.bat
python start.py
pause
