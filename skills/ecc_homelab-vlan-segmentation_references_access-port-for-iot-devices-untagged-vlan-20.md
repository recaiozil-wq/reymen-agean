---
name: ecc_homelab-vlan-segmentation_references_access-port-for-iot-devices-untagged-vlan-20
description: Access port for IoT devices (untagged VLAN 20)
title: "Ecc Homelab Vlan Segmentation References Access Port For Iot Devices Untagged Vlan 20"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Access port for IoT devices (untagged VLAN 20) |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Access port for IoT devices (untagged VLAN 20)
/interface bridge port
add bridge=bridge interface=ether3 pvid=20 frame-types=admit-only-untagged-and-priority-tagged
