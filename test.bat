@echo off
title ReYMeN Test
cd /d "%~dp0"
call venv\Scripts\activate.bat
python test_suite.py
if %ERRORLEVEL% EQU 0 (
    echo Tum testler gecti!
) else (
    echo Testlerde hata var!
)
pause
