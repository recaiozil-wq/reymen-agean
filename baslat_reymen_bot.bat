@echo off
chcp 65001 >nul
cd /d "%~dp0"
set "TELEGRAM_BOT_TOKEN=8774151638:AAFNMVK12XjC-V7TLIM98WGmQgd4KRF72tU"
set "GATEWAY_ALLOW_ALL_USERS=true"
"C:\Users\marko\AppData\Local\Python\pythoncore-3.14-64\python.exe" telegram_bot/bot.py
pause
