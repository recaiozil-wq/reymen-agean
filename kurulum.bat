@echo off
chcp 65001 >nul
title ReYMeN Agent v2.0 - Kurulum

echo ============================================
echo    ReYMeN Agent v2.0 - Kurulum
echo ============================================
echo.

:: ---------- GEREKSINIM KONTROLLERI ----------
echo --- Gereksinim Kontrolleri ---

:: 1. Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Python bulunamadi!
    echo     Adres: https://www.python.org/downloads/
    echo     Windows: python-3.11.x.exe indir, kurarken "Add Python to PATH" isaretle
    pause
    exit /b
)

python -c "import sys; v=sys.version_info; exit(0) if v.major==3 and v.minor>=11 else exit(1)" >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Python 3.11 veya ustu gerekli!
    python --version
    pause
    exit /b
)

for /f "tokens=*" %%i in ('python --version 2^>nul') do set PYVER=%%i
echo [OK] %PYVER%

:: 2. Git
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Git bulunamadi!
    echo     Adres: https://git-scm.com/download/win
    pause
    exit /b
)
for /f "tokens=*" %%i in ('git --version') do set GITVER=%%i
echo [OK] %GITVER%

:: 3. VS Code (opsiyonel)
code --version >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] VS Code var (opsiyonel)
) else (
    echo [--] VS Code yok (gerekli degil, kod duzenleme icin opsiyonel)
)

:: 4. WSL/Ubuntu (opsiyonel)
wsl --version >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] WSL var (opsiyonel - Kali/Linux ozellikleri icin)
) else (
    echo [--] WSL yok (gerekli degil, sadece Linux araclari icin)
)

echo.
echo --- Repo Klonlaniyor ---
if not exist "ReYMeN-Ajan-v2" (
    git clone https://github.com/Watcher-Hermes/ReYMeN-Ajan-v2.git
) else (
    echo ReYMeN-Ajan-v2 zaten var, guncelleniyor...
    cd ReYMeN-Ajan-v2
    git pull
    cd ..
)
cd ReYMeN-Ajan-v2

echo.
echo --- Sanal Ortam ---
if not exist "venv" (
    python -m venv venv
    echo [OK] Sanal ortam olusturuldu
) else (
    echo [OK] Sanal ortam zaten var
)

call venv\Scripts\activate

echo.
echo --- Bagimliliklar Yukleniyor ---
if exist requirements.txt (
    pip install -r requirements.txt
    if %errorlevel% equ 0 (
        echo [OK] Tum paketler yuklendi
    ) else (
        echo [!] Paket yukleme hatasi! Elle dene: pip install -r requirements.txt
    )
) else (
    echo requirements.txt bulunamadi
)

:: Temel paketleri kontrol et
echo.
echo --- Bagimlilik Kontrolu ---
python -c "import requests" >nul 2>&1 && echo [OK] requests || echo [!] requests eksik
python -c "import pytest" >nul 2>&1 && echo [OK] pytest || echo [!] pytest eksik

echo.
echo --- .env Dosyasi ---
if not exist .env (
    echo # ReYMeN - API Anahtarlari > .env
    echo. >> .env
    echo # API anahtarlarini buraya ekle >> .env
    echo # DEEPSEEK_API_KEY=sk-... >> .env
    echo # TELEGRAM_BOT_TOKEN=123456:ABC-... >> .env
    echo [!!] .env dosyasi olusturuldu! API anahtarlarini eklemeyi unutma!
) else (
    echo [OK] .env dosyasi var
)

echo.
echo ============================================
echo    KURULUM TAMAMLANDI!
echo ============================================
echo.
echo KISACA:
echo   VS Code  : Gerekli DEGIL (opsiyonel)
echo   WSL      : Gerekli DEGIL (opsiyonel)
echo   Python   : 3.11+ gerekli - [OK]
echo   Git      : Gerekli - [OK]
echo.
echo KULLANIM:
echo   1. cd ReYMeN-Ajan-v2
echo   2. venv\Scripts\activate
echo   3. python reymen_launcher.py
echo.
echo ONEMLI: .env dosyasina API anahtarlarini ekle!
echo.
pause
