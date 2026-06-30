@echo off
chcp 65001 >nul
title ReYMeN Bot Supervisor
cd /d "C:\Users\marko\Desktop\Reymen Proje\ReYMeN-Ajan"

:: =====================================================================
:: ReYMeN Bot Supervisor — bot_supervisor.py uzerinden 3 bot
:: =====================================================================
:: Her bot kendi profil .env'sinden token okur
:: Crash'te otomatik restart eder
:: =====================================================================

echo [%date% %time%] ReYMeN Bot Supervisor baslatiliyor...
echo.

:: Supervisor modu: 3 bot + crash restart
start /MIN "ReYMeN_Supervisor" cmd /c "cd /d C:\Users\marko\Desktop\Reymen Proje\ReYMeN-Ajan && venv\Scripts\python.exe bot_supervisor.py"

echo Bot Supervisor baslatildi.
echo Supervizoru durdurmak icin: taskkill /f /fi "WINDOWTITLE eq ReYMeN_Supervisor"
echo Tek seferlik calistirmak icin: python bot_supervisor.py --once
