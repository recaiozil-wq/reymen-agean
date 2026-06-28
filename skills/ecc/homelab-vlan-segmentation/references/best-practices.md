---
skill_id: 35a30d27959f
usage_count: 1
last_used: 2026-06-16
---
## Best Practices

- Start with 4 VLANs: Trusted, IoT, Servers, Guest — add more as needed
- Put Pi-hole in the Servers VLAN (192.168.30.x)
- Add a firewall rule allowing DNS (port 53) from all VLANs to the Pi-hole IP — before any RFC1918 block rule
- Test isolation after every rule change: from the IoT VLAN, try to ping a trusted device — it should fail
- Use a management VLAN for switch and AP web UIs and restrict access to the Trusted VLAN only
- Document your VLAN design in a table (VLAN ID, name, subnet, purpose)