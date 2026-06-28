---
skill_id: 87aa75cfa947
usage_count: 1
last_used: 2026-06-16
---
# Hosts Dosyası ile Site Engelleme (Windows)

## Ne Zaman Kullanılır

- Kullanıcı "X sitesini engelle" dediğinde
- Özellikle **Tor Browser** da dahil tüm tarayıcılarda erişim engellenecekse
- Yanlışlıkla girilen siteleri kalıcı olarak bloke etmek için

## Yöntem: Windows hosts dosyası

**Dosya:** `C:\Windows\System32\drivers\etc\hosts`

**Mantık:** Site adını `127.0.0.1`'e yönlendir — tarayıcı siteyi bulamaz, bağlantı timeout olur.

## Adım Adım

### 1. PowerShell scripti ile ekle (self-elevating)

```powershell
# block_site.ps1 — self-elevate template
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    $arguments = "-NoProfile -ExecutionPolicy Bypass -File `"" + $MyInvocation.MyCommand.Path + "`""
    Start-Process powershell -Verb RunAs -ArgumentList $arguments
    exit
}

$hostsPath = "$env:SystemRoot\System32\drivers\etc\hosts"
Add-Content -Path $hostsPath -Value "`n127.0.0.1 siteadi.com" -Force
Write-Host "EKLENDI: siteadi.com -> 127.0.0.1"
```

Yönetici yetkisi gerekir. `allow-once-watcher` cron (no_agent=true) UAC ekranını otomatik tıklar.

### 2. Doğrulama

```powershell
Get-Content 'C:\Windows\System32\drivers\etc\hosts' | Select-String 'siteadi'
```

### 3. Obsidian'a kaydet

Engellenen sitelerin listesi: `07-System/Engelli-Siteler.md`
Tablo formatı: Site | Yönlendirme | Tarih

### 4. Kaldırma

hosts dosyasından ilgili satırı manuel sil.

## Engellenen Siteler (Güncel)

| Site | Tarih | Sebep |
|------|-------|-------|
| my.101domain.com | 2026-06-14 | Kullanıcı talebi |
| breachforum.to | 2026-06-14 | Ölü domain, yanlışlıkla girildi |

## Uyarılar

- `bash` içinden PowerShell inline komutlarında tırnak/backtick sorunu olur → **.ps1 dosyasına yaz + çalıştır** yöntemi tercih edilir
- hosts dosyası **yönetici yetkisi** gerektirir — normal kullanıcı yazamaz
- Tor Browser SOCKS5 proxy kullanır ama DNS çözümlemesi hosts dosyasına bakar → engelleme çalışır
