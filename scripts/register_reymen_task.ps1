$taskName = 'ReYMeN-Botlar'

# Önce varsa eski taski sil
Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue

$action = New-ScheduledTaskAction -Execute 'C:\Users\marko\Desktop\Reymen Proje\ReYMeN-Ajan\venv\Scripts\python.exe' `
    -Argument 'C:\Users\marko\Desktop\Reymen Proje\ReYMeN-Ajan\bot_supervisor.py --once' `
    -WorkingDirectory 'C:\Users\marko\Desktop\Reymen Proje\ReYMeN-Ajan'

$trigger = New-ScheduledTaskTrigger -AtLogOn -User 'marko'

$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 2)

$principal = New-ScheduledTaskPrincipal -UserId 'marko' -LogonType Interactive -RunLevel Limited

Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Force

Write-Host "[OK] Task '$taskName' kaydedildi ve aktif!" -ForegroundColor Green

# Dogrulama
$task = Get-ScheduledTask -TaskName $taskName
Write-Host "[Durum] $($task.State)" -ForegroundColor Cyan
