---
skill_id: 73b68d118685
usage_count: 1
last_used: 2026-06-16
---
## Problem Giderme

- **`VBoxManage: command not found`**: Tam yol kullan: `"C:\Program Files/Oracle/VirtualBox/VBoxManage.exe"`
- **`keyboardputstring` calismiyor**: VM'in calistigini kontrol et: `"VBoxManage.exe" list runningvms`
- **Karmasik komut calismiyor**: Ozel karakterlerden kurtul, komutu basitlestir
- **Cikti gelmiyor**: `sleep` suresini artir, komutun bitmesini bekle
- **USB WiFi Kali'de gorunmuyor**: xHCI acik mi kontrol et (`showvminfo`), filtre dogru mu, VM yeniden baslatildi mi
- **`lsusb`'de var ama `iw dev`'de yok**: Driver yuklenmemis olabilir — `dmesg | grep rt73` ile kontrol et
- **`iwlist wlan0 scanning`: No scan results**: Once `iw reg set DE`, sonra `ip link set wlan0 up`, sonra `iw dev wlan0 scan -u` dene
6. **WiFi adaptor cok yavas / sadece 2.4 GHz**: Ralink RT2501/RT2573 802.11 b/g — 5 GHz desteklemez