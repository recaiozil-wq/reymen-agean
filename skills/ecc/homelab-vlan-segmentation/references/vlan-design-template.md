---
skill_id: bd3e0f15b413
usage_count: 1
last_used: 2026-06-16
---
## VLAN Design Template

```
VLAN  Name        Subnet              Gateway         Purpose
10    trusted     192.168.10.0/24     192.168.10.1    PCs, phones, laptops
20    iot         192.168.20.0/24     192.168.20.1    Smart home devices
30    servers     192.168.30.0/24     192.168.30.1    NAS, Pi, self-hosted
40    guest       192.168.40.0/24     192.168.40.1    Visitor Wi-Fi
99    management  192.168.99.0/24     192.168.99.1    Network gear web UIs
```