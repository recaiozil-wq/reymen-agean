Set WshShell = CreateObject("WScript.Shell")
' Kill zombie sohbet
WshShell.Run "taskkill /PID 51948 /F", 0, True
' Kill kiral38
WshShell.Run "taskkill /PID 45568 /F", 0, True
' Kill reymen
WshShell.Run "taskkill /PID 48532 /F", 0, True
' Kill default
WshShell.Run "taskkill /PID 55080 /F", 0, True
' Kill other sohbet
WshShell.Run "taskkill /PID 51080 /F", 0, True

WScript.Sleep 5000

' Restart gateways (hidden window)
WshShell.Run "cmd /c start /MIN hermes -p kiral38 gateway start", 0, False
WScript.Sleep 2000
WshShell.Run "cmd /c start /MIN hermes -p reymen gateway start", 0, False
WScript.Sleep 2000
WshShell.Run "cmd /c start /MIN hermes gateway start", 0, False
