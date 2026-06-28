---
name: ecc_homelab-vlan-segmentation_references_step-5-assign-gateway-ips
description: "Step 5: Assign gateway IPs"
title: "Ecc Homelab Vlan Segmentation References Step 5 Assign Gateway Ips"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Step 5: Assign gateway IPs |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Step 5: Assign gateway IPs
/ip address
add interface=vlan10 address=192.168.10.1/24
add interface=vlan20 address=192.168.20.1/24
