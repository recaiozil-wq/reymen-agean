---
skill_id: 420d2dc4b8c9
usage_count: 1
last_used: 2026-06-16
---
# Aynı aracın farklı parametrelerini dene (help'te gördüklerinle sınırlı kal)
```

**Kural:** Kullanıcı "help komutu ile yol bul" dediğinde, dış kaynaklardan (web, Tor) çözüm aramadan önce mutlaka önce Kali'de `--help`/`man` ile çözüm ara. Help'te yolu gösteren parametre varsa onu kullan, yoksa alternatif araçları help ile keşfet.

**Örnek akış (bu oturumda test edildi):**
```
iw → "device or resource busy" → iw --help ile wlan0 down/up/set type gör
    → managed moda geç → scan çalışır → S22 PLAS tespit edilir
    → monitor moda dön → airodump-ng ile canlı takip
```

Kali'ye USB Wi-Fi adaptörü takıldığında (RT2501/RT2573 / rt73usb) `wlan0` arayüzü **otomatik oluşmayabilir**. `lsusb` cihazı görür, `lsmod` sürücüyü gösterir ama `ip link show`'da wlan arayüzü yoktur. Bu durumda:

### Arayüzü Elle Oluştur

```bash