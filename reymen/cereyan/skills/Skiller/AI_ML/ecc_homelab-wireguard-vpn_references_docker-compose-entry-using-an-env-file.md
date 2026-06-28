---
name: ecc_homelab-wireguard-vpn_references_docker-compose-entry-using-an-env-file
description: "docker-compose entry using an env file:"
title: "Ecc Homelab Wireguard Vpn References Docker Compose Entry Using An Env File"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | docker-compose entry using an env file: |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# docker-compose entry using an env file:
  ddns-updater:
    image: qmcgaw/ddns-updater
    env_file: ./ddns.env   # store zone_id and token here, not in compose
    restart: unless-stopped
