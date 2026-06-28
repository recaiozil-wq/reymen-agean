---
skill_id: 0580b6dfc0d2
usage_count: 1
last_used: 2026-06-16
---
# Doğrula
iw dev
ip link show wlan0
```

### Monitor Mode (airmon-ng YERİNE iw ile)

`airmon-ng start wlan0` **interaktif prompt sorar** (`Found phy0 with no interfaces assigned, would you like to assign one to it? [y/n]`) ve SSH üzerinden cevap verilemediği için recursion hatasıyla çöker (`Maximum function recursion depth (1000) reached`).

**Doğru yöntem — manuel iw:**
```bash
sudo ip link set wlan0 down
sudo iw dev wlan0 set type monitor
sudo ip link set wlan0 up