@echo off
REM ReYMeN Agent — Telegram Bot Baslatici (Batch)
REM Kullanim: reymen [--once|--stop|--status]
REM Not: Bu batch dosyasi PowerShell'de de calisir.

set PROJE_KOK=C:\Users\marko\Desktop\Reymen Proje\ReYMeN-Ajan
set PYTHON=%PROJE_KOK%\venv\Scripts\python.exe

if "%1"=="--status" goto status
if "%1"=="--stop" goto stop
if "%1"=="--once" goto once
if "%1"=="--web" goto web
if "%1"=="web" goto web
goto start

:start
echo [ReYMeN] Bot Supervisor baslatiliyor...
"%PYTHON%" "%PROJE_KOK%\bot_supervisor.py"
goto end

:once
echo [ReYMeN] Botlar baslatiliyor (arka planda)...
"%PYTHON%" "%PROJE_KOK%\bot_supervisor.py" --once
goto end

:stop
echo [ReYMeN] Botlar durduruluyor...
"%PYTHON%" "%PROJE_KOK%\bot_supervisor.py" --stop
goto end

:status
echo [ReYMeN] Bot durumu:
tasklist /fi "imagename eq python.exe" /v 2>nul | findstr /i "telegram_bot bot_supervisor"
if %errorlevel% neq 0 echo Hicbir bot process'i calismiyor.
goto end

:web
echo [ReYMeN] Hermes Studio baslatiliyor...
start "" http://localhost:8648
"%PYTHON%" "%PROJE_KOK%\reymen_launcher.py" web
goto end

:end
