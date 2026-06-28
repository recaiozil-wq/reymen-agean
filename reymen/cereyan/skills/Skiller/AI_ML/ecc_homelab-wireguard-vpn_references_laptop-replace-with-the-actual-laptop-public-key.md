---
name: ecc_homelab-wireguard-vpn_references_laptop-replace-with-the-actual-laptop-public-key
description: Laptop — replace with the actual laptop public key
title: "Ecc Homelab Wireguard Vpn References Laptop Replace With The Actual Laptop Public Key"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Laptop — replace with the actual laptop public key |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Laptop — replace with the actual laptop public key
PublicKey = <laptop_public_key>
AllowedIPs = 10.8.0.3/32
EOF
sudo chmod 600 /etc/wireguard/wg0.conf
