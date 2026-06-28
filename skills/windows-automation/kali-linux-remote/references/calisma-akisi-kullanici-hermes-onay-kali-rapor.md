---
skill_id: 6cc53e382127
usage_count: 1
last_used: 2026-06-16
---
## Calisma Akisi (Kullanici -> ReYMeN -> Onay -> Kali -> Rapor)

```
Kullanici -> "sudo arp-scan -l" yazar
    |
ReYMeN -> Kullaniciya sorar: "arp-scan ile 192.168.0.0/24 taranacak, onayliyor musun?"
    |
Kullanici -> "evet" yazar (klavyeden onay)
    |
ReYMeN -> SSH ile Kali'ye komutu gonderir
    |
Kali -> komutu calistirir, cikti SSH uzerinden ReYMeN'e doner
    |
ReYMeN -> kendi terminalinde sonucu tablo/ozet olarak raporlar
```

**KRITIK:** HER ADIMDA kullanicidan onay alinir. "evet" veya "tamam" cevabini bekle. Cevap gelmezse (bir kere bekle, suskunluk = devam kuralina uy) DEVAM ETME.

### WiFi Tarama Stratejisi — İki Yöntem Arasında Seçim

SSH üzerinden Kali'de WiFi taraması yaparken **iki yöntem** arasında seçim yap:

| Yöntem | Hız | Çıktı Boyutu | Hangi Mod | Kullanım Amacı |
|--------|-----|-------------|-----------|----------------|
| `iw dev wlan0 scan` (managed) | Çok hızlı (~2-5 sn) | Küçük (~5-50 KB) | managed | **ÖNCELİKLİ** — hızlı tarama, SSID/Ağ tespiti, sinyal seviyesi |
| `airodump-ng` (monitor) | Yavaş, sürekli güncellenir | Çok büyük (MB-GB) | monitor | Sadece canlı takip / paket yakalama / handshake |

#### Yöntem 1 — `iw dev wlan0 scan` (Tercih Edilen, Öncelikli)

En hızlı ve güvenilir yöntem. managed modda çalışır, tüm kanalları tarar, kompakt çıktı verir:

```bash