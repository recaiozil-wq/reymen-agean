---
name: ecc_homelab-wireguard-vpn_references_generate-server-keypair-create-files-with-private-permission
description: Generate server keypair — create files with private permissions from the start
title: "Ecc Homelab Wireguard Vpn References Generate Server Keypair Create Files With Private Permission"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Generate server keypair — create files with private permissions from the start |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Generate server keypair — create files with private permissions from the start
sudo mkdir -p /etc/wireguard
sudo sh -c 'umask 077; wg genkey > /etc/wireguard/server_private.key'
sudo sh -c 'wg pubkey < /etc/wireguard/server_private.key > /etc/wireguard/server_public.key'
