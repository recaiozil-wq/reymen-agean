---
name: ecc_homelab-vlan-segmentation_references_access-port-for-trusted-devices-untagged-vlan-10
description: Access port for trusted devices (untagged VLAN 10)
title: "Ecc Homelab Vlan Segmentation References Access Port For Trusted Devices Untagged Vlan 10"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Access port for trusted devices (untagged VLAN 10) |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Access port for trusted devices (untagged VLAN 10)
/interface bridge port
add bridge=bridge interface=ether2 pvid=10 frame-types=admit-only-untagged-and-priority-tagged
