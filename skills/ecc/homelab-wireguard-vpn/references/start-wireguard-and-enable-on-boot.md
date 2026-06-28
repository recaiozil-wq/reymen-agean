---
skill_id: 6fe765ba081a
usage_count: 1
last_used: 2026-06-16
---
# Start WireGuard and enable on boot
sudo wg-quick up wg0
sudo systemctl enable wg-quick@wg0
```