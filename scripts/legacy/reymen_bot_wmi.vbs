Set WshShell = CreateObject("WScript.Shell")
wd = "C:\Users\marko\OneDrive\Desktop\Reymen Proje\hermes_projesi"
pythonExe = "C:\Users\marko\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe"
botScript = "C:\Users\marko\OneDrive\Desktop\Reymen Proje\hermes_projesi\telegram_bot\bot.py"

' WMI ile baslat (ReYMeN job object'inden bagimsiz)
cmd = """" & pythonExe & """ """ & botScript & """"
WshShell.CurrentDirectory = wd
Set objWMIService = GetObject("winmgmts:\\.\root\cimv2")
Set objStartup = objWMIService.Get("Win32_Process")
intReturn = objStartup.Create(cmd, wd, Null, intProcessID)

If intReturn = 0 Then
    CreateObject("WScript.Shell").Popup "ReYMeN Bot baslatildi! PID: " & intProcessID, 3, "ReYMeN", 64
Else
    CreateObject("WScript.Shell").Popup "HATA! Kod: " & intReturn, 5, "ReYMeN", 16
End If
