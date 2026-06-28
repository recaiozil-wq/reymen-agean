---
name: ecc_homelab-wireguard-vpn_references_3-is-ip-forwarding-enabled-on-the-server
description: 3.
title: "Ecc Homelab Wireguard Vpn References 3 Is Ip Forwarding Enabled On The Server"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | 3.0 |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# 3. Is IP forwarding enabled on the server?
cat /proc/sys/net/ipv4/ip_forward  # Should be 1
