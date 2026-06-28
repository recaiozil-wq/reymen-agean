---
skill_id: 02b34085be18
usage_count: 1
last_used: 2026-06-16
---
# airodumping ile tarama
sudo airodump-ng wlan0
```

### Bilinen Sorunlar

- **"Wrong frame size" dmesg hataları** → Anten fiziksel olarak takılı değil veya zayıf sinyal. `airodump-ng` CH 0'da takılı kalır, hiçbir BSSID görmez. Çözüm: anteni kontrol et veya alternatif Wi-Fi yöntemi kullan.
- **Sinyal yoksa airodump boş döner** — bu adaptör sorunu değil, ortam/anten sorunudur. Windows host'taki Wi-Fi kartı ile alternatif yöntem dene (netsh wlan show networks mode=bssid).
- **USB passthrough sorunları:** VirtualBox USB filtresi doğru ayarlanmış olmalı, yoksa cihaz VM'den host'a atlayıp durur.
- **rt73usb sürücüsü:** RT2501/RT2573 için doğru sürücü `rt73usb` (rt2501usb DEĞİL). `modprobe rt2501usb` çalışmaz.

### Hızlı Kurtarma (Arayüz Silindiyse)

Arayüz yanlışlıkla silindiyse (`sudo iw dev wlan0mon del` veya `sudo iw dev wlan0 del`):

```bash