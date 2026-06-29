---
name: ecc_uncloud_references_service-dns-internal
description: Service DNS (Internal)
title: "Ecc Uncloud References Service Dns Internal"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Service DNS (Internal) |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

## Service DNS (Internal)

Services inside the cluster resolve each other by name:

| DNS name | Resolves to |
|----------|------------|
| `service-name` | Any healthy container |
| `service-name.internal` | Same |
| `rr.service-name.internal` | Round-robin |
| `nearest.service-name.internal` | Machine-local first |
