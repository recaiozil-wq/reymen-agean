@echo off
chcp 65001 >nul
title ReYMeN Agent v1.0 - Tam Kurulum

echo ============================================
echo    ReYMeN Agent v1.0 - Tam Kurulum
echo ============================================
echo.
echo NOT: ReYMeN bagimsiz bir ajandir, Hermes gerektirmez.
echo.
echo ============================================

:: ---------- 1. GEREKSINIM KONTROLLERI ----------
set ADIM=0

:: 1.1 Python
set /a ADIM+=1
echo ^(1/4^) Python kontrolu...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [!!] Python bulunamadi! Yukleniyor...
    winget install Python.Python.3.11 --silent --accept-package-agreements
    if %errorlevel% neq 0 (
        echo [!] Otomatik basarisiz! Suradan el ile indir:
        echo     https://www.python.org/downloads/release/python-3119/
        echo     Kurarken "Add Python to PATH" isaretle
        pause
        exit /b
    )
)
python -c "import sys; exit(0) if sys.version_info >= (3,11) else exit(1)" >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Python 3.11+ gerekli!
    python --version
    pause
    exit /b
)
for /f "tokens=*" %%i in ('python --version 2^>nul') do set PYVER=%%i
echo [OK] %PYVER%

:: 1.2 Git
set /a ADIM+=1
echo ^(2/4^) Git kontrolu...
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [!!] Git bulunamadi! Yukleniyor...
    winget install Git.Git --silent --accept-package-agreements
    if %errorlevel% neq 0 (
        echo [!] Basarisiz! https://git-scm.com/download/win
        pause
        exit /b
    )
)
for /f "tokens=*" %%i in ('git --version') do set GITVER=%%i
echo [OK] %GITVER%

:: ---------- 2. REPO + VENV ----------
set /a ADIM+=1
echo ^(3/4^) Repo ve Python ortami...

:: Proje dizinini bul
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

if not exist "reymen_launcher.py" (
    if exist "ReYMeN-Ajan" (
        cd ReYMeN-Ajan
    ) else (
        echo [!!] Proje dosyalari bulunamadi!
        echo     Bu script ReYMeN-Ajan klasoru icinde calistirilmali.
        echo     veya: git clone https://github.com/Watcher-Hermes/ReYMeN-Ajan-v2.git
        pause
        exit /b
    )
)

if not exist "reymen_venv" (
    python -m venv reymen_venv
    if !errorlevel! neq 0 (
        echo [!!] Sanal ortam olusturulamadi!
        pause
        exit /b
    )
    echo [OK] Sanal ortam: reymen_venv
)

call reymen_venv\Scripts\activate

:: pip paketleri
if exist requirements.txt (
    pip install -r requirements.txt --quiet
) else (
    pip install requests python-dotenv --quiet
)
if !errorlevel! equ 0 (
    echo [OK] Paketler yuklendi
) else (
    echo [!] Paket hatasi! Elle: pip install -r requirements.txt
    pause
    exit /b
)

:: ---------- 3. .env API ANAHTARLARI ----------
set /a ADIM+=1
echo ^(4/4^) API anahtarlari...

if not exist ".env" (
    (
        echo # ============================================================
        echo # ReYMeN Agent - API Anahtarlari
        echo # Bu dosyayi duzenleyip kendi anahtarlarini ekle
        echo # ============================================================
        echo.
        echo # === ZORUNLU: En az bir LLM provider ===
        echo # DeepSeek (en uyumlu, tavsiye edilen)
        echo # Kayit: https://platform.deepseek.com/api_keys
        echo DEEPSEEK_API_KEY=buraya_yaz
        echo.
        echo # === OPSIYONEL: Diger providerlar (yedek) ===
        echo # DeepSeek kredisi bitince otomatik gecer
        echo # OPENROUTER_API_KEY=buraya_yaz
        echo # XAI_API_KEY=buraya_yaz
        echo # GROQ_API_KEY=buraya_yaz
        echo.
        echo # === OPSIYONEL: Telegram Bot ===
        echo # BotFather'dan al: https://t.me/BotFather
        echo # /newbot komutu ile yeni bot olustur
        echo # Alinan tokeni buraya yapistir
        echo TELEGRAM_BOT_TOKEN=buraya_yaz
        echo.
        echo # === OPSIYONEL: Harici servisler ===
        echo # FIRECRAWL_API_KEY=buraya_yaz
        echo # PERPLEXITY_API_KEY=buraya_yaz
        echo # FAL_KEY=buraya_yaz
    ) > .env
    echo.
    echo ============================================
    echo  .env dosyasi olusturuldu!
    echo ============================================
    echo.
    echo  SIMDI SU ISLEMLERI YAP:
    echo.
    echo  1. Asagidaki dosya notepad ile acilacak
    echo  2. DEEPSEEK_API_KEY satirina anahtarini yaz
    echo     (https://platform.deepseek.com/api_keys)
    echo  3. Kaydet ve kapat
    echo.
    echo  NOT: Anahtar yoksa https://platform.deepseek.com adresinden
    echo  ucretsiz hesap ac, API key olustur.
    echo.
    pause
    start notepad .env
)

echo.
echo ============================================
echo    KURULUM TAMAMLANDI!
echo ============================================
echo.
echo  KULLANIM:
echo.
echo  --- SECENEK 1: Terminal'de calistir ---
echo      reymen_venv\Scripts\activate
echo      python reymen_launcher.py
echo.
echo  --- SECENEK 2: Telegram Bot ---
echo      1. .env dosyasina TELEGRAM_BOT_TOKEN ekle
echo      2. BotFather'dan token al (/newbot)
echo      3. Baslat:
echo         reymen_venv\Scripts\activate ^&^& python reymen/ag/telegram_bot.py
echo.
echo  --- SSS / HATA COZUMU ---
echo.
echo  "DEEPSEEK_API_KEY kredisi bitti" (402):
echo     - .env'ye OPENROUTER_API_KEY ekle
echo     - Fallback otomatik gecer
echo.
echo  "409 Conflict" (Telegram bot baglanamiyor):
echo     - BotFather'a git -> /mybots -> botunu sec
echo     - API Token -> Revoke -> Yeni token al
echo     - Yeni tokeni .env'ye yaz, tekrar baslat
echo.
echo  "ModuleNotFoundError":
echo     - reymen_venv\Scripts\activate
echo     - pip install -r requirements.txt
echo.
echo  GitHub: https://github.com/Watcher-Hermes/ReYMeN-Ajan-v2
echo.
pause
