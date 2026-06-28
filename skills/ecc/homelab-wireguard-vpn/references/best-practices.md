---
skill_id: 35a30d27959f
usage_count: 1
last_used: 2026-06-16
---
## Best Practices

- Generate a unique keypair per client device — never reuse keys
- Use split tunneling (`AllowedIPs = <home subnets>`) for mobile
- Set `PersistentKeepalive = 25` on all mobile clients
- Use DDNS if your ISP assigns a dynamic IP; store credentials in env files, not inline
- Use scoped iptables forwarding rules (inbound on wg0 only) rather than a blanket FORWARD ACCEPT
- Add Pi-hole's IP as `DNS =` in client configs to get ad blocking over the VPN
- Rotate the server keypair periodically and update all client configs