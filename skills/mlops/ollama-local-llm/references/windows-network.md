---
skill_id: c5730a36ac89
usage_count: 1
last_used: 2026-06-16
---
# Windows network enumeration notes

Use stdlib first. The first reliable implementation here was:

- IP via `socket.gethostbyname(socket.gethostname())`
- MAC via `uuid.getnode()`
- Cross-check with `ipconfig /all` and `getmac`
- ARP only for LAN peers, not local adapters

Avoid ad-hoc parsing of Windows console tables in generated scripts; it is fragile.