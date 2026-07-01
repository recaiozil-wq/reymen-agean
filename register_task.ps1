$taskName = 'ReYMeN-Botlar'
Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue

$action = New-ScheduledTaskAction -Execute "C:\Users\marko\Desktop\Reymen Proje\ReYMeN-Ajan\venv\Scripts\python.exe" -Argument "C:\Users\marko\Desktop\Reymen Proje\ReYMeN-Ajan\bot_supervisor.py --once" -WorkingDirectory "C:\Users\marko\Desktop\Reymen Proje\ReYMeN-Ajan"
$trigger = New-ScheduledTaskTrigger -AtLogOn
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 2)
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive

Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Force | Out-Null

$task = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
if ($task) {
    Write-Host "[OK] Task '$taskName' kaydedildi - Durum: $($task.State)"
} else {
    Write-Host "[HATA] Task kaydedilemedi"
    exit 1
}
