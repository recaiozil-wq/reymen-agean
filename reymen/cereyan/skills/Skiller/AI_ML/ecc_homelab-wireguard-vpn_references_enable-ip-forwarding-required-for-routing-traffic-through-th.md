---
name: ecc_homelab-wireguard-vpn_references_enable-ip-forwarding-required-for-routing-traffic-through-th
description: Enable IP forwarding (required for routing traffic through the server)
title: "Ecc Homelab Wireguard Vpn References Enable Ip Forwarding Required For Routing Traffic Through Th"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Enable IP forwarding (required for routing traffic through the server) |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Enable IP forwarding (required for routing traffic through the server)
echo "net.ipv4.ip_forward=1" | sudo tee /etc/sysctl.d/99-wireguard.conf
sudo sysctl --system
