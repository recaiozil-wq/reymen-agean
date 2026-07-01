schtasks /Create /SC ONLOGON /TN "ReYMeN-Botlar" /TR "'C:\Users\marko\Desktop\Reymen Proje\ReYMeN-Ajan\venv\Scripts\python.exe' 'C:\Users\marko\Desktop\Reymen Proje\ReYMeN-Ajan\bot_supervisor.py' --once" /RU marko /IT /F
if %errorlevel% equ 0 (
    echo [OK] Task ReYMeN-Botlar kaydedildi
) else (
    echo [HATA] Task kaydedilemedi
)
