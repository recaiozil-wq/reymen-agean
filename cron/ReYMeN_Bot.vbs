' ReYMeN_Bot.vbs — Bilgisayar açılışında ReYMeN bot'unu arka planda başlatır
' Startup klasörüne koyulur (shell:startup)

Dim oShell
Set oShell = CreateObject("Wscript.Shell")

' Python path
Dim pythonExe, botScript, workDir
pythonExe = "C:\Users\marko\AppData\Local\Python\PythonCore-3.14-64\python.exe"
botScript = "C:\Users\marko\OneDrive\Desktop\Reymen Proje\hermes_projesi\bot.py"
workDir = "C:\Users\marko\OneDrive\Desktop\Reymen Proje\hermes_projesi"

' Bot'u gizli pencerede başlat
oShell.CurrentDirectory = workDir
oShell.Run """" & pythonExe & """ """ & botScript & """", 0, False
