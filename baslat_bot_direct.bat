@echo off
chcp 65001 >nul
cd /d "%~dp0"
setlocal enabledelayedexpansion
for /f "tokens=1,* delims==" %%a in ('findstr /b "TELEGRAM_BOT_TOKEN" .env') do set "TELEGRAM_BOT_TOKEN=%%b"
start /B python telegram_bot/bot.py
echo Bot baslatildi.
