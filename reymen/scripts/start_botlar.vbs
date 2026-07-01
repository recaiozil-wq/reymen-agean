Set WshShell = CreateObject("WScript.Shell")
' ReYMeN Bot Baslatma — Startup icin
' Kullanimi: Bu dosyayi shell:startup klasorune kopyala

hermes_path = "%USERPROFILE%\AppData\Local\hermes\hermes-agent\venv\Scripts\hermes.exe"

WshShell.Run hermes_path & " gateway --profile default", 0, False
WshShell.Run hermes_path & " gateway --profile reymen", 0, False
WshShell.Run hermes_path & " gateway --profile kiral38", 0, False
