---
skill_id: 11538070d22f
usage_count: 1
last_used: 2026-06-16
---
# Windows Forensic — Trace Locations

## Event Log
| Kanal | Dosya | Tipik Boyut |
|-------|-------|-------------|
| Security | `C:\Windows\System32\winevt\Logs\Security.evtx` | 20-40 MB |
| System | `C:\Windows\System32\winevt\Logs\System.evtx` | 4-8 MB |
| Application | `C:\Windows\System32\winevt\Logs\Application.evtx` | 4-10 MB |
| Windows PowerShell | `C:\Windows\System32\winevt\Logs\Windows PowerShell.evtx` | 1-15 MB |
| PowerShell/Operational | `C:\Windows\System32\winevt\Logs\Microsoft-Windows-PowerShell%4Operational.evtx` | 1-5 MB |
| Sysmon (varsa) | `C:\Windows\System32\winevt\Logs\Microsoft-Windows-Sysmon%4Operational.evtx` | Değişken |

**Komut satırı log'u (Event ID 4688):**
- `Security.evtx` içinde kaydedilir
- Process creation: "python.exe", "powershell.exe", "VeraCrypt.exe" görünür
- Komut satırı argümanları da kaydedilebilir (GPO'ya bağlı)
- PowerShell ScriptBlock logging: script içeriğini de kaydeder

## USBSTOR
```
Registry: HKLM\SYSTEM\CurrentControlSet\Enum\USBSTOR\...
  → Her USB için VID/PID + Seri No + İlk/ Son takılış tarihi
Registry: HKLM\SYSTEM\MountedDevices\...
  → Sürücü harfi → cihaz eşlemesi
```

## Network
| Kaynak | Yol | İçerik |
|--------|-----|--------|
| WiFi profilleri | `netsh wlan show profiles` | SSID listesi |
| NLA (Network List) | `HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\NetworkList\Profiles\` | Bağlanılan tüm ağlar |
| SRUM | `C:\Windows\System32\sru\SRUDB.dat` | Uygulama bazında ağ kullanımı (admin gerek) |
| DNS cache | `ipconfig /displaydns` | Ziyaret edilen domain'ler |
| ARP table | `arp -a` | Yerel ağdaki cihazlar |
| Active connections | `netstat -n` | Anlık TCP bağlantıları |

## OneDrive
```
Process: OneDrive.exe (her zaman çalışır, otomatik başlar)
Yol: C:\Users\marko\OneDrive\
İçerik: Tüm senkronize dosyalar (bulutta da aynen durur)
Risk: Obsidian vault burada ise tüm notlar bulutta düz metin
```

## VirtualBox
| Dosya | Konum | İçerik |
|-------|-------|--------|
| VBox.log | `C:\Users\marko\VirtualBox VMs\<VM>\Logs\` | Açılış/kapanış, ağ trafiği, hatalar |
| VBoxHardening.log | Aynı dizin | Güvenlik kontrolleri |
| selectorwindow.log | `C:\Users\marko\.VirtualBox\` | VirtualBox yöneticisi |
| VBoxSVC.log | `C:\Users\marko\.VirtualBox\` | VirtualBox servisi |
| VirtualBox.xml | `C:\Users\marko\.VirtualBox\` | VM listesi, Host-Only ağ yapılandırması |
| .vbox | `C:\Users\marko\VirtualBox VMs\<VM>\` | VM yapılandırması (ISO yolu, RAM, CPU) |
| Dhcpd.config | `C:\Users\marko\.VirtualBox\` | Host-Only DHCP ayarları |
| Dhcpd.leases | `C:\Users\marko\.VirtualBox\` | DHCP kiralama kayıtları |

**VBox.log'dan çıkan bilgiler:**
- Host işletim sistemi sürümü (Windows 11, build numarası)
- RAM miktarı (toplam + kullanılabilir)
- Secure Boot durumu
- VM çalışma süresi
- VM ağ trafiği istatistikleri (kaç paket gönderilmiş/alınmış)
- Paylaşımlı klasör listesi
- ISO dosya yolu

## PowerShell History
```
Dosya: C:\Users\marko\AppData\Roaming\Microsoft\Windows\PowerShell\PSReadLine\ConsoleHost_history.txt
İçerik: PowerShell'de yazılan HER KOMUT (düz metin)
Risk: VeraCrypt şifreleri, API anahtarları, dosya yolları
Temizlik: Dosyayı sil veya boşalt
```

## Disk Encryption
```powershell
# BitLocker durumunu kontrol
manage-bde -status C:
Get-BitLockerVolume -MountPoint "C:" -ErrorAction SilentlyContinue

# Windows edition (Pro = BitLocker var)
(Get-WmiObject Win32_OperatingSystem).Caption
```
