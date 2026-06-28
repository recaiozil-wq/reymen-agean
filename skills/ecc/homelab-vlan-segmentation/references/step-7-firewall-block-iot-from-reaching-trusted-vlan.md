---
skill_id: 852494962b08
usage_count: 1
last_used: 2026-06-16
---
# Step 7: Firewall — block IoT from reaching trusted VLAN
/ip firewall filter
add chain=forward src-address=192.168.20.0/24 dst-address=192.168.10.0/24 \
    action=drop comment="Block IoT to Trusted"
```