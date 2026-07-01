<#
.SYNOPSIS
    ReYMeN Agent — Telegram Bot Baslatici (PowerShell)
.DESCRIPTION
    ReYMeN Telegram botlarini baslatir.
    Kullanim:
        .\reymen.ps1            # Bot supervisor'i baslat (Pasa_38 + ReYMeN_ReYMeNbot)
        .\reymen.ps1 --once     # Supervisor olmadan baslat
        .\reymen.ps1 --stop     # Tum botlari durdur
        .\reymen.ps1 --status   # Bot durumunu goster
#>

param(
    [string]$Action = "start"
)

$ProjeKok = "C:\Users\marko\Desktop\Reymen Proje\ReYMeN-Ajan"
$Python = Join-Path $ProjeKok "venv\Scripts\python.exe"
$Supervisor = Join-Path $ProjeKok "bot_supervisor.py"

# PowerShell'e ozgu PATH sorununu coz
$env:PATH = "$ProjeKok\venv\Scripts;$env:PATH"

switch ($Action) {
    "start" {
        Write-Host "🚀 ReYMeN Bot Supervisor baslatiliyor..." -ForegroundColor Green
        & $Python $Supervisor
    }
    "--once" {
        Write-Host "🚀 ReYMeN Botlar baslatiliyor (supervisor'siz)..." -ForegroundColor Green
        & $Python $Supervisor --once
    }
    "--stop" {
        Write-Host "⏹ ReYMeN Botlar durduruluyor..." -ForegroundColor Yellow
        & $Python $Supervisor --stop
    }
    "--status" {
        Write-Host "📊 ReYMeN Bot Durumu:" -ForegroundColor Cyan
        Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object {
            $_.CommandLine -match "telegram_bot|bot_supervisor"
        } | Format-Table Id, ProcessName, @{Name="Command";Expression={$_.CommandLine -replace '^.+\\([^\\]+)$','$1'}}
        
        if ((Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -match "telegram_bot" }).Count -eq 0) {
            Write-Host "❌ Hicbir bot process'i calismiyor" -ForegroundColor Red
        }
    }
    default {
        Write-Host "Kullanim: .\reymen.ps1 [--once|--stop|--status]" -ForegroundColor Yellow
    }
}
