@echo off
chcp 65001 >nul
cd /d "C:\Users\marko\Desktop\Reymen Proje\ReYMeN-Ajan"

REM ReYMeN bot'larini sessiz baslat (pencere gosterme)
start /B "" python telegram_bot/ai_bot.py
start /B "" python telegram_bot/ai_bot.py
