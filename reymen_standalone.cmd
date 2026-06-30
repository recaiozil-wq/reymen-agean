@echo off
REM ============================================================================
REM  ReYMeN Agent — Bagimsiz Baslatma (Hermes'siz)
REM  Kullanim:  reymen_standalone.cmd
REM ============================================================================
setlocal enabledelayedexpansion

set "PROJE=%~dp0"
cd /d "%PROJE%"

echo ============================================
echo  ReYMeN Agent — Bagimsiz Mod
echo  Hermes baglantisi OLMADAN calisir
echo ============================================
echo.

REM ReYMeN venv'ini kullan
set "VENV_PYTHON=%PROJE%venv\Scripts\python.exe"

if not exist "%VENV_PYTHON%" (
    echo [HATA] venv bulunamadi: %VENV_PYTHON%
    pause
    exit /b 1
)

REM Python yolundan Hermes'i temizle
set "PYTHONPATH="
for /f "tokens=*" %%p in ('where python 2^>nul') do (
    echo %%p | findstr /i "hermes" >nul
    if errorlevel 1 (
        set "SAFE_PYTHON=%%p"
    )
)

echo [OK] Python: %VENV_PYTHON%
echo [OK] Proje: %PROJE%
echo.

:menu
echo.
echo === ReYMeN Bagimsiz Mod ===
echo  1) Telegram Bot'u baslat
echo  2) REPL (komut satiri) baslat
echo  3) Test (bagimsizlik dogrulama)
echo  4) Cikis
echo.
set /p secim="Secim [1-4]: "

if "%secim%"=="1" goto bot
if "%secim%"=="2" goto repl
if "%secim%"=="3" goto test
if "%secim%"=="4" exit /b 0
goto menu

:bot
echo.
echo [BASLATILIYOR] ReYMeN Multi-Bot (3 bot) ...
echo.
echo Baslatiliyor: Kral_38, Pasa_38, ReYMeN_¥_♤
echo.
"%VENV_PYTHON%" run_bots.py
pause
goto menu

:repl
echo.
echo [BASLATILIYOR] ReYMeN REPL ...
echo.
"%VENV_PYTHON%" reymen_launcher.py
pause
goto menu

:test
echo.
echo [TEST] ReYMeN bagimsizlik dogrulama ...
"%VENV_PYTHON%" -c "
import sys
sys.path.insert(0, '.')
print('Beyin test ediliyor...')
from reymen.cereyan.beyin import Beyin
from reymen.sistem.main import CONFIG
b = Beyin(config=CONFIG)
print(f'[OK] Beyin: {b.provider}/{b.model}')
from reymen.cereyan.conversation_loop import ConversationLoop
loop = ConversationLoop(beyin=b, max_tur=3)
s = loop.coz('test')
print(f'[OK] coz(): basarili={s[\"basarili\"]}')
s2 = loop.run_conversation('1+1 kac eder? sadece sayi')
print(f'[OK] API: {s2.get(\"yanit\",\"\")}')
print()
print('=== REYMEN HERMES\'SIZ CALISIYOR! ===')
"
echo.
pause
goto menu
