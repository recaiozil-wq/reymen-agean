@echo off
REM ============================================================================
REM  reymen.cmd — ReYMeN Agent Bagimsiz Komutu
REM  Kullanim: reymen [--once|--stop|--status|--bot|--repl]
REM ============================================================================
setlocal

set "REYMEN_PROJE=C:\Users\marko\Desktop\Reymen Proje\ReYMeN-Ajan"
set "REYMEN_VENV_PY=%REYMEN_PROJE%\venv\Scripts\python.exe"

if not exist "%REYMEN_VENV_PY%" (
    echo [HATA] ReYMeN venv bulunamadi: %REYMEN_VENV_PY%
    pause
    exit /b 1
)

cd /d "%REYMEN_PROJE%"

if "%1"=="--bot" goto bot
if "%1"=="--once" goto once
if "%1"=="--stop" goto stop
if "%1"=="--status" goto status
if "%1"=="--repl" goto repl
goto help

:bot
REM Bot supervisor (surekli)
"%REYMEN_VENV_PY%" "%REYMEN_PROJE%\bot_supervisor.py"
goto end

:once
REM Botlari baslat (arka planda, supervisor'siz)
"%REYMEN_VENV_PY%" "%REYMEN_PROJE%\bot_supervisor.py" --once
goto end

:stop
REM Botlari durdur
"%REYMEN_VENV_PY%" "%REYMEN_PROJE%\bot_supervisor.py" --stop
goto end

:status
REM Bot durumu
tasklist /fi "imagename eq python.exe" /v 2>nul | findstr /i "telegram_bot bot_supervisor"
if %errorlevel% neq 0 echo [BILGI] Hicbir bot process'i calismiyor.
goto end

:repl
REM ReYMeN REPL (interactive)
"%REYMEN_VENV_PY%" "%REYMEN_PROJE%\reymen_launcher.py"
goto end

:help
echo ReYMeN Agent — Kullanim:
echo   reymen --bot      Bot supervisor'i baslat
echo   reymen --once     Botlari arka planda baslat
echo   reymen --stop     Tum botlari durdur
echo   reymen --status   Bot durumunu goster
echo   reymen --repl     ReYMeN REPL'i baslat
echo   reymen --help     Bu yardim mesaji
goto end

:end
