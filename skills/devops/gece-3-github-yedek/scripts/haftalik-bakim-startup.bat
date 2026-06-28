@echo off
REM HERMES HAFTALIK BAKIM STARTUP
REM Bilgisayar acilinca calisir, gun Carsamba ise flag olusturur

for /f "tokens=3" %%a in ('wmic path win32_localtime get dayofweek') do set gun=%%a
set gun=%gun: =%

if "%gun%"=="3" (
    echo [ReYMeN] Carsamba - Haftalik bakim flag'i olusturuluyor...
    echo %date% %time% > "%USERPROFILE%\AppData\Local\hermes\haftalik-bakim.flag"

    REM Gateway calismiyorsa baslat
    schtasks /Query /TN ReYMeN_Gateway /FO CSV 2>nul | findstr /C:"Running" >nul
    if errorlevel 1 (
        echo [ReYMeN] Gateway baslatiliyor...
        powershell -NoProfile -Command "Start-ScheduledTask -TaskName ReYMeN_Gateway"
    ) else (
        echo [ReYMeN] Gateway zaten calisiyor
    )
    echo [ReYMeN] Hazir - Cron job bakimi tetikleyecek.
) else (
    echo [ReYMeN] Bugun Carsamba degil (%gun%), bakim atlandi.
)
