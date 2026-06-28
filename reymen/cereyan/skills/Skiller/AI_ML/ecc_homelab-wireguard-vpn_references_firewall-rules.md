---
name: ecc_homelab-wireguard-vpn_references_firewall-rules
description: "Firewall rules:"
title: "Ecc Homelab Wireguard Vpn References Firewall Rules"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Firewall rules: |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Firewall rules:
  WAN → Allow UDP port 51820 inbound (so clients can reach the server)
  WireGuard interface → Allow traffic to LAN networks you want reachable
```
