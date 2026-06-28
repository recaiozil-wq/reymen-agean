---
skill_id: f8f68e31bf2d
usage_count: 1
last_used: 2026-06-16
---
# Additional exceptions for IoT devices that need specific local services:
  Insert before Rule 2 (the RFC1918 block):
    Protocol: TCP
    Source: IoT net
    Destination: 192.168.30.x port 8123  ← Home Assistant
    Action: Allow
```