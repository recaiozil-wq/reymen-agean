---
name: ecc_homelab-wireguard-vpn_references_multi-subnet-split-tunnel-most-common-homelab-use-case
description: "Multi-subnet split tunnel (most common homelab use case):"
title: "Ecc Homelab Wireguard Vpn References Multi Subnet Split Tunnel Most Common Homelab Use Case"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Multi-subnet split tunnel (most common homelab use case): |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Multi-subnet split tunnel (most common homelab use case):
  AllowedIPs = 192.168.10.0/24, 192.168.20.0/24, 192.168.30.0/24, 10.8.0.0/24
  Routes all your VLANs through the tunnel; internet stays direct.
```
