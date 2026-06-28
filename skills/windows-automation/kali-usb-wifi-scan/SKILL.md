---
name: kali-usb-wifi-scan
description: USB WiFi adaptörünü Kali VM'e passthrough yap, çevredeki ağları VBoxManage keyboardputstring ile tara ve Kali ekranında göster.
title: "Kali Usb Wifi Scan"

audience: user
tags: [automation, windows]
category: windows-automation---

# Kali USB WiFi ile Çevre Ağ Taraması

Ralink RT2501/RT2573 (veya benzer) USB WiFi adaptörünü VirtualBox Kali VM'e passthrough yapıp `iw dev wlan0 scan` ile çevredeki 2.4GHz ağları bulma ve VBoxManage keyboardputstring ile Kali terminalinde gösterme.

## Ön Koşullar

- Kali VM "kal" çalışıyor olmalı (VirtualBox)
- USB WiFi adaptörü takılı (Ralink RT2573, rt73usb driver)
- Guest Additions yüklü
- Bridged network ile Kali'ye SSH erişimi (opsiyonel, hız için)

## Adımlar

### 1. USB Passthrough'u Kontrol Et

```powershell
# USB cihazı Windows'ta görünüyor mu?
"C:\Program Files\Oracle\VirtualBox\VBoxManage.exe" list usbhost

# VM'ye USB filtre ekle (tek seferlik)
"C:\Program Files\Oracle\VirtualBox\VBoxManage.exe" usbfilter add 0 --target "kal" --name "Ralink WiFi" --vendorid 148f --productid 2573

# xHCI kontrolcü aktif mi?
"C:\Program Files\Oracle\VirtualBox\VBoxManage.exe" modifyvm "kal" --usbxhci on
```

### 2. VM'de WiFi Adaptörünü Doğrula

```bash
# Kali'de SSH ile kontrol
sshpass -p 'kali' ssh kali@192.168.0.XX 'lsusb | grep -i ralink'

# Çıktı: Bus 001 Device 002: ID 148f:2573 Ralink Technology, Corp. RT2501/RT2573 Wireless Adapter

# Arayüz adını bul
sshpass -p 'kali' ssh kali@192.168.0.XX 'iw dev'
# Çıktı: wlan0 (veya wlx...)
```

### 3. WiFi Taraması

```bash
# Arayüzü yukarı çek ve bölge ayarla
sshpass -p 'kali' ssh kali@192.168.0.XX 'sudo ip link set wlan0 up'
sshpass -p 'kali' ssh kali@192.168.0.XX 'sudo iw reg set TR'

# Tüm kanalları tara
sshpass -p 'kali' ssh kali@192.168.0.XX 'sudo iw dev wlan0 scan'
```

**ÖNEMLİ**: `sudo iw dev wlan0 scan -u` kullanma — `-u` flag'i sadece mevcut kanalı tarar. Düz `scan` tüm kanalları (1-13) tarar.

### 4. Sonuçları Kali Ekranında Göster (VBoxManage)

```powershell
# Ana başlık
"C:\Program Files\Oracle\VirtualBox\VBoxManage.exe" controlvm "kal" keyboardputstring "echo '=== WI-FI TARAMA SONUCLARI ==='"
"C:\Program Files\Oracle\VirtualBox\VBoxManage.exe" controlvm "kal" keyboardputstring "`n"

# Her ağ için ayrı satır
"C:\Program Files\Oracle\VirtualBox\VBoxManage.exe" controlvm "kal" keyboardputstring "echo '1) SSID_ADI (Kanal X, Sinyal: -YY dBm)'"
"C:\Program Files\Oracle\VirtualBox\VBoxManage.exe" controlvm "kal" keyboardputstring "`n"
```

### 4. WiFi Konum Takibi (Trilateration / Fingerprinting)

Hedef cihazın SSID ve sinyal bilgisi ile konum kestirimi yapılabilir.

**MAC Rastgeleleştirme Sorunu:** Modern telefonlar (Samsung One UI 6+) her taramada farklı MAC gönderir. Çözüm stratejisi:

1. **SSID bazlı filtreleme:** Hedef cihazın SSID'si sabittir (ör: "S 22 PLAS")
2. **Çevre AP profili:** Değişmeyen BSSID'lerle çevre ağ parmak izi çıkar
3. **Sinyal gücü karşılaştırması:** RSSI değeri (±5 dBm tolerans) ile aynı cihazı tanı
4. **Kanal bilgisi:** Kanal numarası sabitse cihaz aynıdır

**MAC rastgeleleştirme nasıl kapatılır (Samsung One UI 6+):**
Ayarlar → Wi-Fi → "S 22 PLAS" → Gelişmiş → MAC Adresi Türü → "Telefon MAC'i" (Random MAC değil)

**Tespit akışı:**
```bash
# 1. Çevredeki tüm ağları tara
sshpass -p 'kali' ssh kali@<ip> 'sudo iw dev wlan0 scan' | \
  grep -E "SSID:|signal:|freq:|BSSID" | paste - - - -

# 2. SSID'ye göre filtrele
sshpass -p 'kali' ssh kali@<ip> 'sudo iw dev wlan0 scan 2>&1' | \
  grep -A 5 "S 22 PLAS"

# 3. Çevre AP'lerin BSSID'leri sabit → parmak izi çıkarma
sshpass -p 'kali' ssh kali@<ip> 'sudo iw dev wlan0 scan 2>&1' | \
  grep -B 2 "SSID:" | grep "BSSID"
```

SSH ile `sudo iw dev wlan0 scan` çıktısından SSID'leri çek:

```bash
sshpass -p 'kali' ssh kali@192.168.0.XX 'sudo iw dev wlan0 scan 2>&1' | grep "SSID:"
```

## Önemli Noktalar

- **Ralink RT2573 sadece 2.4GHz b/g** — 5GHz ağları göremez
- **İlk taramada az ağ çıkması normal** — WiFi adaptörü önce bir kanala kilitlenir, tüm kanalları taraması zaman alır
- **`iw dev wlan0 scan -u` sadece mevcut kanalı tarar** — çoğu ağı kaçırırsın
- **`iw dev wlan0 scan` tüm kanalları tarar** — doğru sonuç için bunu kullan
- **Country kodu 00 (ayarlanmamış) ise** pasif tarama modunda çalışır, çoğu ağı bulamaz. `iw reg set TR` veya `iw reg set DE` ile ayarla
- **Telefon hotspot'ları** genelde kanal 11 veya 6'da açar, düz tarama ile bulunur

## Monitor Mode — airmon-ng Çökme Sorunu ve Çözümü

`airmon-ng start wlan0` **SSH üzerinden interaktif prompt sorduğu için çöker:**
```
Found phy0 with no interfaces assigned, would you like to assign one to it? [y/n]
```
Bu prompt SSH üzerinden cevaplanamaz → `Maximum function recursion depth (1000) reached` hatası.

**Doğru yöntem — manuel iw ile:**

```bash
sudo ip link set wlan0 down
sudo iw dev wlan0 set type monitor
sudo ip link set wlan0 up

# Doğrula
iw dev wlan0 info   # type monitor olmalı
```

**Tarama:** Monitor modda `iw dev wlan0 scan` çalışmaz (`Operation not supported -95`). Bunun yerine:
```bash
sudo airodump-ng wlan0
```

**ÖNEMLİ:** airmon-ng kullanma. Her zaman `iw` ile manuel yap. Eğer zaten yanlışlıkla `iw dev wlan0 del` silindiyse:
```bash
sudo iw phy phy0 interface add wlan0 type managed   # yeniden oluştur
```

## Problem Giderme

| Sorun | Çözüm |
|-------|-------|
| USB adaptörü Kali'de görünmüyor | VM kapalıyken USB filtre ekle, xHCI etkinleştir |
| "No scan results" | `iw reg set TR` dene, `ip link set wlan0 up` yap |
| Sinyal zayıf | Adaptörü USB 2.0 portuna tak (3.0 bazen sorun çıkarır) |
| Sadece 1-2 ağ görüyor | `-u` flag'i olmadan dene (tüm kanallar) |
| SSH çalışmıyor | Guest Additions yükle, bridged network kullan |
| airmon-ng recursion hatası | airmon-ng kullanma → `iw` ile manuel monitor mod |
| airodump CH 0 takılı, BSSID yok | **Anten fiziksel olarak takılı değil.** Ralink RT73 USB adaptörlerinde anten ayrı takılır. `dmesg`'de "Wrong frame size" hatası varsa çözüm: anteni kontrol et. |
