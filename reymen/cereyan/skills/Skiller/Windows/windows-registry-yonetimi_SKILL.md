--- 
title: Windows Kayıt Defteri Yönetimi
name: windows-registry-yonetimi
description: Windows Registry anahtarlarını okuma, yazma, yedekleme ve geri yükleme işlemleri
tags: [windows, registry, kayit, sistem, yonetim]
---

# Windows Kayıt Defteri Yönetimi

| 5N1K | Açıklama |
|------|----------|
| Kim | ReYMeN bot kullanıcıları |
| Ne | Windows Registry (kayıt defteri) anahtarlarını okur, yazar, yedekler ve geri yükler |
| Nerede | reymen/cereyan/skills/Skiller/Windows/ |
| Ne Zaman | Uygulama ayarları, startup konfigürasyonu veya sistem tweak'leri gerektiğinde |
| Neden | Windows ayarlarının çoğu Registry'de saklanır — GUI'siz değişiklik için gereklidir |
| Nasıl | PowerShell `Get-ItemProperty` / `Set-ItemProperty` komutları ile yönetilir |

## Temel Komutlar

| İşlem | PowerShell Komutu |
|-------|-------------------|
| Oku | `Get-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion"` |
| Yaz | `Set-ItemProperty -Path "HKCU:\Control Panel\Desktop" -Name "MenuShowDelay" -Value 200` |
| Yedekle | `reg export HKCU\Software\MyApp backup.reg` |
| Geri Yükle | `reg import backup.reg` |
| Sil | `Remove-ItemProperty -Path "HKCU:\..." -Name "Setting"` |

## Kritik Yollar

- `HKLM:\SOFTWARE\` — Makine geneli ayarlar (admin gerekir)
- `HKCU:\Software\` — Kullanıcı bazlı ayarlar
- `HKLM:\SYSTEM\CurrentControlSet\Services\` — Servis konfigürasyonu
- `HKCU:\Control Panel\Desktop\` — Masaüstü davranışı

## Güvenlik

- Registry değişikliği ÖNCESİ her zaman yedek al (`reg export`)
- Değişiklik etkisi hemen görünür, reboot gerektirmez
- System düzeyi değişikliklerde admin yetkisi kontrolü yap
