
> **Kategori:** Windows

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Windows ajanı |
| **Ne?** | Windows Automation_Ag Taramasi Arp Vs Nmap_References_Kablosuz Ve Kablolu Ag Karsilastirmasi |
| **Nerede?** | Windows/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

# Kablosuz vs Kablolu Ag Tarama Karsilastirmasi

Bu oturumda Kali VM'in hem ethernet (bridged eth1) hem de USB WiFi (wlan0)
arayuzleri uzerinden tarama yapildi. Gozlemlenen farklar:

## Kablolu Ag (eth1, 192.168.0.0/24)
- arp-scan: 7 cihaz, 1.8 sn
- nmap -sn: 6 cihaz, 3.5 sn
- ARP her cihazda calisir — en kapsamli yontem
- MAC adresinden IP bulma: `arp -a | grep "08-00-27"`

## Kablosuz Ag (wlan0, cevre taramasi)
- iwlist wlan0 scanning: PASSIVE-SCAN modunda (country=00), hic sonuc yok
- iw dev wlan0 scan -u: Aktif tarama, 2 ag bulundu
- Bolge kodu (regulatory domain) olmadan aktif tarama MUMKUN DEGIL

### Bolge Kodu Etkisi

| country | Mod | Sonuc |
|---------|-----|-------|
| 00 (varsayilan) | PASSIVE-SCAN | Hic ag bulunamaz |
| DE (Almanya) | ACTIVE-SCAN + PASSIVE | Tum aglar gorunur |
| TR (Turkiye) | ACTIVE-SCAN + PASSIVE | Tum aglar gorunur |

### Bulunan Aglar (oturum verisi)

| SSID | BSSID | Kanal | Frekans | Sinyal | Guvenlik | Istasyon |
|------|-------|-------|---------|--------|----------|----------|
| TURKSAT-KABLONET-U0JG-2.4G | 18:48:59:2a:c1:30 | 1 | 2412 MHz | -22 dBm | WPA2-PSK | 5 |
| FiberHGW_TPB320 | 8c:86:dd:3a:b3:26 | 1 | 2412 MHz | -70 dBm | WPA2-PSK | bilinmiyor |

### Donanim

- Ralink RT2501/RT2573 (ID 148f:2573)
- Driver: rt73usb, Firmware: rt73.bin
- 2.4 GHz b/g, maks 54 Mbps
- Kali'de Bus 001 Device 002
