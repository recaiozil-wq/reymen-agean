---
name: ecc_homelab-wireguard-vpn_references_start-wireguard-and-enable-on-boot
description: Start WireGuard and enable on boot
title: "Ecc Homelab Wireguard Vpn References Start Wireguard And Enable On Boot"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Start WireGuard and enable on boot |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Start WireGuard and enable on boot
sudo wg-quick up wg0
sudo systemctl enable wg-quick@wg0
```
