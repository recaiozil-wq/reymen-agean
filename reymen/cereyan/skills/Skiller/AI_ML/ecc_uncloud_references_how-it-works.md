---
name: ecc_uncloud_references_how-it-works
description: How It Works
title: "Ecc Uncloud References How It Works"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | How It Works |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

## How It Works

Uncloud runs Docker services across peer machines connected by a WireGuard mesh. Each machine is an equal cluster member; services communicate on the overlay network and Caddy runs globally to terminate public HTTP/HTTPS traffic. Compose files can use Uncloud extensions for ingress, placement, and generated Caddy configuration, while the `uc` CLI handles image distribution, scheduling, scaling, logs, and cluster state.
