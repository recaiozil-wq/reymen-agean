$projeKok = "C:\Users\marko\Desktop\Reymen Proje\ReYMeN-Ajan"
$launcher = Join-Path $projeKok "launch_bots.py"
Start-Process python -ArgumentList $launcher -WorkingDirectory $projeKok -WindowStyle Hidden
Write-Output "ReYMeN botlari baslatildi."
