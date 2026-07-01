@echo off
REM ReYMeN Bot Baslatma — Startup icin
REM Kullanimi: Bu dosyayi shell:startup klasorune kopyala
REM (Win+R -> shell:startup -> yapistir)

set HERMES=%USERPROFILE%\AppData\Local\hermes\hermes-agent\venv\Scripts\hermes.exe

echo [ReYMeN] Botlar baslatiliyor...
start /b /min "" "%HERMES%" gateway --profile default
start /b /min "" "%HERMES%" gateway --profile reymen
start /b /min "" "%HERMES%" gateway --profile kiral38
echo [ReYMeN] 3 bot baslatildi.
