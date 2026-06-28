---
skill_id: 5224c0a99f6d
usage_count: 1
last_used: 2026-06-16
---
# 1. Monitor moda geç
ssh kali "sudo ip link set wlan0 down && sudo iw dev wlan0 set type monitor && sudo ip link set wlan0 up"