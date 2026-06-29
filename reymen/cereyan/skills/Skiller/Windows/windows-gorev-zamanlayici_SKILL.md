--- 
title: Windows Görev Zamanlayıcı
name: windows-gorev-zamanlayici
description: Windows Task Scheduler ile periyodik görevler, tetikleyiciler ve aksiyonlar yönetimi
tags: [windows, gorev, zamanlayici, scheduler, otomasyon]
---

# Windows Görev Zamanlayıcı

| 5N1K | Açıklama |
|------|----------|
| Kim | ReYMeN bot kullanıcıları |
| Ne | Windows Task Scheduler ile periyodik görevler (script, exe, email) oluşturur ve yönetir |
| Nerede | reymen/cereyan/skills/Skiller/Windows/ |
| Ne Zaman | Belirli aralıklarla çalışması gereken otomasyon görevleri olduğunda |
| Neden | Hermes cron Windows'ta bash'a bağımlıdır; Task Scheduler native çözümdür |
| Nasıl | PowerShell `New-ScheduledTask` cmdlet'leri veya `schtasks.exe` ile yönetilir |

## Komut Kullanımı (schtasks.exe)

| İşlem | Komut |
|-------|-------|
| Oluştur | `schtasks /create /tn "GörevAdı" /tr "powershell.exe -File script.ps1" /sc daily /st 09:00` |
| Çalıştır | `schtasks /run /tn "GörevAdı"` |
| Durdur | `schtasks /end /tn "GörevAdı"` |
| Sil | `schtasks /delete /tn "GörevAdı" /f` |
| Listele | `schtasks /query /fo LIST /v` |

## Zamanlama Türleri

| Tür | Açıklama | Örnek |
|-----|----------|-------|
| `/sc once` | Tek seferlik | `schtasks /create /tn "Backup" /tr "script.bat" /sc once /st 23:00 /sd 2026-06-30` |
| `/sc daily` | Her gün | `/sc daily /st 09:00` |
| `/sc weekly` | Haftalık | `/sc weekly /d MON /st 09:00` |
| `/sc minute` | Her N dakika | `/sc minute /mo 30` |
| `/sc onlog` | Event log tetiklemesi | `/sc onlog /ec System /mo "1000"` |

## Güvenlik

- Görevler SYSTEM veya kullanıcı yetkisiyle çalışır
- Yüksek yetki gerekiyorsa `/ru SYSTEM` eklenir
- Loglar Event Viewer > Task Scheduler altında tutulur
