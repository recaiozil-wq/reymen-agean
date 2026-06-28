---
skill_id: a82d2ba23f3d
usage_count: 1
last_used: 2026-06-16
---
# 2. Belli bir hedef BSSID'yi izle (arka planda, timeout ile)
ssh kali "sudo timeout 60 airodump-ng wlan0 --bssid <HEDEF_BSSID> --channel <CH> -w /tmp/airodump_out --output-format csv --write-interval 5 2>/dev/null"