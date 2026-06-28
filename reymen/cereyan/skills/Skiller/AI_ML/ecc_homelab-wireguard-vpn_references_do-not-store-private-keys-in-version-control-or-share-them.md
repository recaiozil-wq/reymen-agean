---
name: ecc_homelab-wireguard-vpn_references_do-not-store-private-keys-in-version-control-or-share-them
description: Do not store private keys in version control or share them
title: "Ecc Homelab Wireguard Vpn References Do Not Store Private Keys In Version Control Or Share Them"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Do not store private keys in version control or share them |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Do not store private keys in version control or share them
sudo tee /etc/wireguard/wg0.conf << 'EOF'
[Interface]
Address = 10.8.0.1/24              # VPN subnet — server gets .1
ListenPort = 51820
PrivateKey = <paste_server_private_key_here>
