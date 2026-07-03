Set WshShell = CreateObject("WScript.Shell")
WshShell.Run """C:\Users\marko\AppData\Local\hermes\hermes-agent\venv\Scripts\hermes.exe"" -p kiral38 gateway start", 0, False
WScript.Sleep 3000
Set WshShell = Nothing
