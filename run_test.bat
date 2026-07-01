@echo off
cd /d "C:\Users\marko\Desktop\Reymen Proje\ReYMeN-Ajan"
"C:\Users\marko\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe" test_standalone.py
if %errorlevel% neq 0 (
    echo HATA kodu: %errorlevel%
    pause
)
