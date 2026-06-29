Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = "C:\Users\marko\Desktop\Reymen Proje\ReYMeN-Ajan"
WshShell.Run "python run_reymen_bots.py", 0, False
