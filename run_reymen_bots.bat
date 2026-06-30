@echo off
chcp 65001 >nul
cd /d "C:\Users\marko\Desktop\Reymen Proje\ReYMeN-Ajan"

:: Bu bot su anda bot_supervisor.py ile yonetiliyor.
:: Supervisor: 3 bot, 3 farkli token, crash'te restart.
echo ReYMeN bot supervisor ile baslatiliyor...
call baslat_tum_botlar.bat
