@echo off
chcp 65001 >nul
title ReYMeN Agent Kurulumu

echo ============================================
echo    ReYMeN Agent v2.0 - Kurulum
echo ============================================
echo.

:: 1. Python kontrol
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [1/5] Python bulunamadi! python.org'dan indirin.
    pause
    exit /b
)
echo [1/5] Python: OK

:: 2. Repo klonla
echo [2/5] Repo klonlaniyor...
git clone https://github.com/Watcher-Hermes/ReYMeN-Ajan-v2.git
cd ReYMeN-Ajan-v2

:: 3. Sanal ortam
echo [3/5] Sanal ortam olusturuluyor...
python -m venv venv
call venv\Scripts\activate

:: 4. Paketler
echo [4/5] Paketler yukleniyor...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Pip hatasi! pip install -r requirements.txt calistirin.
)

:: 5. .env olustur
echo [5/5] .env dosyasi olusturuluyor...
if not exist .env (
    echo # ReYMeN - API Anahtarlari > .env
    echo DEEPSEEK_API_KEY=deepseek_api_keyinizi_girin >> .env
    echo TELEGRAM_BOT_TOKEN=telegram_bot_tokeninizi_girin >> .env
    echo.
    echo NOT: .env dosyasi olusturuldu. API anahtarlarinizi ekleyin!
)

echo.
echo ============================================
echo    KURULUM TAMAMLANDI!
echo ============================================
echo.
echo Kullanmak icin:
echo    cd ReYMeN-Ajan-v2
echo    venv\Scripts\activate
echo    python reymen_launcher.py
echo.
echo ÖNCE .env dosyasina API anahtarlarini ekle!
echo.
pause
