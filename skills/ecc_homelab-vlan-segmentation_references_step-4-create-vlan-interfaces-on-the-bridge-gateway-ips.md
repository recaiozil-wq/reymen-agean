---
name: ecc_homelab-vlan-segmentation_references_step-4-create-vlan-interfaces-on-the-bridge-gateway-ips
description: "Step 4: Create VLAN interfaces on the bridge (gateway IPs)"
title: "Ecc Homelab Vlan Segmentation References Step 4 Create Vlan Interfaces On The Bridge Gateway Ips"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Step 4: Create VLAN interfaces on the bridge (gateway IPs) |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Step 4: Create VLAN interfaces on the bridge (gateway IPs)
/interface vlan
add interface=bridge name=vlan10 vlan-id=10
add interface=bridge name=vlan20 vlan-id=20
