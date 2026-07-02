@echo off
REM ReYMeN Bot Supervisor — Windows Startup
REM Bu dosyayi baslat: WIN+R → shell:startup → kopyala

cd /d "C:\Users\marko\Desktop\Reymen Proje\ReYMeN-Ajan"
start /B /MIN "" "%USERPROFILE%\AppData\Roaming\uv\python\cpython-3.11-windows-x86_64-none\python.exe" "reymen\sistem\bot_supervisor.py" --once
