@echo off
title ReYMeN Doctor
cd /d "%~dp0"
call venv\Scripts\activate.bat
python reyment.py doctor
pause
