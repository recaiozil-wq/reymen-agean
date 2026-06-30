@echo off
chcp 65001 >nul
title ReYMeN Tray
cd /d "%~dp0"
echo ReYMeN Desktop (sistem tepsisi) baslatiliyor...
call venv\Scripts\python.bat -m reymen.desktop.launcher tray
