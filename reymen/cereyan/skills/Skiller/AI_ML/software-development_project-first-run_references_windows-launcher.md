---
name: software-development_project-first-run_references_windows-launcher
description: Windows .bat Launcher Template
title: "Software Development Project First Run References Windows Launcher"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Windows .bat Launcher Template |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Windows .bat Launcher Template

## Purpose

A multi-mode Windows batch launcher for Python projects that have:
- A ReAct agent (main.py)
- A web dashboard (start.py --dashboard-only)
- A gateway/telegram service (start.py --agent-only)
- An orchestrator that runs everything (start.py --all)

## Template

```batch
@echo off
title R>eYMeN — Otonom Ajan
chcp 65001 >nul
cd /d "%~dp0"

echo.
echo  ╔══════════════════════════════════════════╗
echo  ║           PROJECT_NAME                   ║
echo  ║    Description Line                      ║
echo  ╚══════════════════════════════════════════╝
echo.

if "%1"=="--help" goto :help
if "%1"=="-h" goto :help
if "%1"=="" goto :menu

:arg_mode
if "%1"=="start" goto :start_all
if "%1"=="agent" goto :start_agent
if "%1"=="dashboard" goto :start_dashboard
if "%1"=="gateway" goto :start_gateway
if "%1"=="doctor" goto :doctor
echo Bilinmeyen komut: %1
goto :help

:menu
echo  Kullanim:
echo    run.bat start        — Tum servisleri baslat
echo    run.bat agent        — Sadece ReAct ajani (CLI)
echo    run.bat dashboard    — Sadece Web UI
echo    run.bat gateway      — Sadece Gateway
echo    run.bat doctor       — Sistem saglik kontrolu
echo    run.bat --help       — Bu yardim mesaji
echo.
goto :end

:start_all
echo  [1/3] Bagimliliklar kontrol ediliyor...
python -c "import requests, fastapi, dotenv" 2>nul
if errorlevel 1 (
    echo  ⚠  Bagimliliklar eksik, yukleniyor...
    pip install -r requirements.txt
)
echo  ✅ Bagimliliklar hazir.
echo.
echo  [2/3] .env kontrol ediliyor...
python -c "from pathlib import Path; p=Path('.env'); print('✅ .env mevcut' if p.exists() else '⚠️ .env bulunamadi!')"
echo.
echo  [3/3] Servisler baslatiliyor...
python start.py --all
goto :end

:start_agent
python main.py
goto :end

:start_dashboard
python start.py --dashboard-only
goto :end

:start_gateway
python start.py --agent-only
goto :end

:doctor
python -c "
from pathlib import Path
import sys
k = Path('.')
print(f'📁 Proje: {k.resolve()}')
print(f'   Python: {sys.version.split()[0]}')
print(f'   Dosya: {len(list(k.glob(\"*.py\")))} Python dosyasi')
env = k / '.env'
if env.exists():
    d = env.read_text(encoding='utf-8')
    satirlar = [s for s in d.split(chr(10)) if s.strip() and not s.startswith('#') and '=' in s]
    print(f'📄 .env: {len(satirlar)} degisken tanimli')
    for s in satirlar:
        ad, val = s.split('=', 1)
        durum = '✅' if val.strip() and val.strip() != '***' else '⚠️'
        print(f'   {durum} {ad.strip()}=...')
"
goto :end

:help
echo  RUN.BAT — Kullanim:
echo    run.bat start        — Tum servisleri baslat
echo    run.bat agent        — Sadece ReAct ajani
echo    run.bat dashboard    — Sadece Web UI
echo    run.bat gateway      — Sadece Gateway
echo    run.bat doctor       — Saglik kontrolu
echo    run.bat --help       — Bu mesaj
goto :end

:end
echo.
```

## Key Patterns

- **`chcp 65001 >nul`** — UTF-8 support for Turkish/Unicode characters in the terminal
- **`cd /d "%~dp0"`** — Change to the script's own directory (so .bat works from any path)
- **`python -c "import ..." 2>nul`** — Silent dependency check without installing
- **`if errorlevel 1`** — Detect import failure and auto-install
- **`%1` argument dispatch** — Simple argument-based mode switching
- **Doctor inline** — Embed health check in Python, not external script

## Common Pitfalls

1. **Path spaces** — Use double quotes around `%~dp0` paths
2. **Python venv** — If the project uses a venv, the .bat should activate it first: `call venv\Scripts\activate.bat`
3. **Admin rights** — Some operations (port binding < 1024) need admin. Check with `NET SESSION >nul 2>&1`
4. **`chcp 65001`** is needed for emoji/Unicode in Python output on Turkish Windows
