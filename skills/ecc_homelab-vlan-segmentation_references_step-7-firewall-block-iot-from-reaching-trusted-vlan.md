---
name: ecc_homelab-vlan-segmentation_references_step-7-firewall-block-iot-from-reaching-trusted-vlan
description: "Step 7: Firewall — block IoT from reaching trusted VLAN"
title: "Ecc Homelab Vlan Segmentation References Step 7 Firewall Block Iot From Reaching Trusted Vlan"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Step 7: Firewall — block IoT from reaching trusted VLAN |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Step 7: Firewall — block IoT from reaching trusted VLAN
/ip firewall filter
add chain=forward src-address=192.168.20.0/24 dst-address=192.168.10.0/24 \
    action=drop comment="Block IoT to Trusted"
```
