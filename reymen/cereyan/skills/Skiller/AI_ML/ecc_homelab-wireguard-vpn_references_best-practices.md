---
name: ecc_homelab-wireguard-vpn_references_best-practices
description: Best Practices
title: "Ecc Homelab Wireguard Vpn References Best Practices"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Best Practices |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

## Best Practices

- Generate a unique keypair per client device — never reuse keys
- Use split tunneling (`AllowedIPs = <home subnets>`) for mobile
- Set `PersistentKeepalive = 25` on all mobile clients
- Use DDNS if your ISP assigns a dynamic IP; store credentials in env files, not inline
- Use scoped iptables forwarding rules (inbound on wg0 only) rather than a blanket FORWARD ACCEPT
- Add Pi-hole's IP as `DNS =` in client configs to get ad blocking over the VPN
- Rotate the server keypair periodically and update all client configs
