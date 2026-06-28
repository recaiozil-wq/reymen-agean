---
name: ecc_homelab-wireguard-vpn_references_run-on-the-client-or-on-the-server-and-transfer-the-private-
description: "Run on the client, or on the server and transfer the private key securely — never in plaintext"
title: "Ecc Homelab Wireguard Vpn References Run On The Client Or On The Server And Transfer The Private "
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Run on the client, or on the server and transfer the private key securely — never in plaintext |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Run on the client, or on the server and transfer the private key securely — never in plaintext
umask 077
wg genkey | tee phone_private.key | wg pubkey > phone_public.key
