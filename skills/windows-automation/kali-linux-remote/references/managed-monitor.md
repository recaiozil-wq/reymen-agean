---
skill_id: 9e906ac8a2bc
usage_count: 1
last_used: 2026-06-16
---
# managed → monitor
sudo ip link set wlan0 down
sudo iw dev wlan0 set type monitor
sudo ip link set wlan0 up
sleep 1