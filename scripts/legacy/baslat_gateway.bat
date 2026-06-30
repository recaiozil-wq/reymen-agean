@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ========================================
echo   ReYMeN Gateway Baslatma
echo ========================================

REM .env'den TELEGRAM_BOT_TOKEN oku
for /f "tokens=1,* delims==" %%a in ('findstr /b "TELEGRAM_BOT_TOKEN" .env') do set "TELEGRAM_BOT_TOKEN=%%b"
echo  Token okundu: %TELEGRAM_BOT_TOKEN:~0,12%...

REM Stale PID temizle
if exist .ReYMeN\gateway.pid (
    set /p OLDPID=<.ReYMeN\gateway.pid
    echo  Eski PID: %OLDPID% - temizleniyor...
    taskkill /F /PID %OLDPID% 2>nul
    del .ReYMeN\gateway.pid 2>nul
)

REM Eski bot PID'leri temizle
taskkill /F /IM python.exe /FI "WINDOWTITLE eq bot*" 2>nul

REM gateway_state.json sil
if exist gateway_state.json del gateway_state.json 2>nul

echo.
echo  Gateway baslatiliyor...
echo  NOT: Terminal acik kalmalidir.
echo  Kapatmak icin Ctrl+C
echo.

REM Token ile ortam degiskenini set et
set TELEGRAM_BOT_TOKEN=%TELEGRAM_BOT_TOKEN%

REM Gateway runner'i baslat
python gateway_runner.py
