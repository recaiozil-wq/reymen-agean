---
skill_id: 58ba34f5136b
usage_count: 1
last_used: 2026-06-16
---
# Check VM NICs
VBoxManage showvminfo <name> | grep -E "NIC|Network"
```

Common configurations:
- **NAT only**: VM gets 10.0.2.15, host sees nothing. Requires port forwarding for inbound connections.
- **Host-Only**: Host and VM on same private subnet (e.g. 192.168.56.0/24). Easier SSH.
- **NAT + Host-Only**: Best of both.

### 4. Remote access options

| Method | Requires | Notes |
|--------|----------|-------|
| SSH | NAT port forwarding **OR** Host-Only adapter | Kali default user often `kali`/`kali` |
| VRDP (RDP) | `--vrde on` + port | VM must be **powered off** to modify |
| Shared clipboard | Guest Additions installed | One-way: Host→Guest or bidirectional |