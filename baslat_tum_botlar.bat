@echo off
chcp 65001 >nul
title ReYMeN Tum Botlar
cd /d "C:\Users\marko\Desktop\Reymen Proje\ReYMeN-Ajan"

:: Pasa_38 (ana bot)
start /B /MIN "" "C:\Users\marko\Desktop\Reymen Proje\ReYMeN-Ajan\venv\Scripts\python.exe" reymen/ag/telegram_bot.py

:: Kral_38 (cron bot)
start /B /MIN "" cmd /c "cd /d C:\Users\marko\Desktop\Reymen Proje\ReYMeN-Ajan && set PYTHONPATH=. && C:\Users\marko\Desktop\Reymen Proje\ReYMeN-Ajan\venv\Scripts\python.exe telegram_bot/bot.py"

:: ReYMeN_Bot (AI bot)
start /B /MIN "" cmd /c "cd /d C:\Users\marko\Desktop\Reymen Proje\ReYMeN-Ajan && set PYTHONPATH=. && C:\Users\marko\Desktop\Reymen Proje\ReYMeN-Ajan\venv\Scripts\python.exe telegram_bot/ai_bot.py"
