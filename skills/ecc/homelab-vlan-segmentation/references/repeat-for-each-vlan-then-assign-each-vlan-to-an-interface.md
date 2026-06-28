---
skill_id: e99290ae98a5
usage_count: 1
last_used: 2026-06-16
---
# Repeat for each VLAN, then assign each VLAN to an interface:
Interfaces → Assignments → Add
  Select the VLAN you created → click Add
  Enable the interface, set IP to gateway address (192.168.20.1/24)
```

### DHCP for Each VLAN

```
Services → DHCP Server → Select your VLAN interface

  Enable DHCP
  Range: 192.168.20.100 to 192.168.20.254
  DNS Servers: 192.168.30.2  ← Pi-hole IP if you have one
```

### Firewall Rules (pfSense/OPNsense)

```