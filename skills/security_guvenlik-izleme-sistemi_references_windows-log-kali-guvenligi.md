
> **Kategori:** Guvenlik

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Kali ajanı |
| **Ne?** | Security_Guvenlik Izleme Sistemi_References_Windows Log Kali Guvenligi |
| **Nerede?** | Guvenlik/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

# Windows Log + Kali VM Operasyonel Güvenliği

## Windows Log'ları Kali Kullanıcısını Ele Vermez

| Windows'un gördüğü | Görmediği |
|---|---|
| VirtualBox.exe çalıştı | Kali'de hangi nmap taraması yapıldı |
| VM kapatıldı/açıldı | Hangi exploit çalıştırıldı |
| USB WiFi adaptörü takıldı | aircrack-ng ile hangi ağ tarandı |
| Dosya host'a kopyalandı | Metasploit'te hangi payload kullanıldı |

## Asıl Riskler (Log'dan Daha Kritik)

| Risk | Açıklama | Çözüm |
|---|---|---|
| **Defender** | Kali'den host'a exploit/zararlı dosya taşırsan algılar | Zararlı dosyaları Kali içinde tut, host'a kopyalama |
| **Paylaşılan Klasör** | VirtualBox paylaşımlı klasörü, Kali'den Windows'a köprüdür. Defender paylaşılan klasöre yazılan her dosyayı tarar | Exploit/payload transferi için paylaşılan klasör kullanma — SSH/SCP kullan |
| **IP/Identity** | VPN/Tor kapalıyken sızma testi yaparsan kendi IP'nden bağlanırsın | Anonimlik gerektiren işlemler için Tor + Kali VM kullan |
| **Açık Portlar** | Windows'ta açık portlar (135, 445) NAT arkasında güvende | Portları kontrol et: `netstat -ano \| Select-String LISTENING` |

## Windows Log Yolları

| Log | Yol | Ne Kaydeder |
|---|---|---|
| Security.evtx | `C:\Windows\System32\winevt\Logs\` | Giriş, dosya silme (audit açıksa) |
| System.evtx | `C:\Windows\System32\winevt\Logs\` | Servis durdurma/başlatma |
| PowerShell.evtx | `C:\Windows\System32\winevt\Logs\` | PowerShell komutları |
| Defender Scans | `C:\ProgramData\Microsoft\Windows Defender\Scans\` | Tarama ve tehdit kayıtları |

## Son Port Taramasi (2026-06-11)

Firewall: Block (tum profiller, NotConfigured = varsayilan Block)
NAT arkasinda: Evet (192.168.x.x)

### 0.0.0.0'da dinleyen (her arayuz - potansiyel LAN erisimi)
| Port | Servis | Firewall | Risk |
|------|--------|----------|:----:|
| 135/tcp | RPC (Windows core) | Block (Allow kurali yok) | ✅ |
| 445/tcp | SMB | Block | ✅ |
| 7680/tcp | Windows Update Delivery Opt. | Allow (beklenen) | ✅ |
| 27036/tcp | Steam | Block | ✅ |
| 49664-54288 | Windows dinamik portlar | Block | ✅ |

### 127.0.0.1'de dinleyen (localhost - guvenli)
5037(ADB), 5554/5555(Android emulator), 11434(Ollama),
7000/8080/8091/8100(Hermes gateway/web), 8554(Android),
5939, 6402, 7681 — hepsi localhost, disariya kapali.

### Paylasimli Klasor Durumu (2026-06-11)
VirtualBox Kali VM: `<none>` — en guvenli durum.

## Tor Browser Trace Cleanup

Tor kullanimi sonrasi iz kalmamasi icin:
- Skill: `tor-browser-arama` → Iz Temizleme bolumu
- Script: `C:\Users\marko\hermes_iz_temizle.py`
- Startup bat: `C:\Users\marko\hermes_tor_cleanup.bat`
- Startup shortcut: `Hermes_Tor_Temizleme.lnk` (Startup klasorunde)
- Pagefile: `ClearPageFileAtShutdown = 1` olarak ayarlandi

Daha detayli temizlik bilgisi icin `tor-browser-arama` skill'ine bak.
