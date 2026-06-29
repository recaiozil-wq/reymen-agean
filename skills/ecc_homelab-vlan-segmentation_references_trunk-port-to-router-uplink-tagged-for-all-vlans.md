---
name: ecc_homelab-vlan-segmentation_references_trunk-port-to-router-uplink-tagged-for-all-vlans
description: Trunk port to router/uplink (tagged for all VLANs)
title: "Ecc Homelab Vlan Segmentation References Trunk Port To Router Uplink Tagged For All Vlans"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Trunk port to router/uplink (tagged for all VLANs) |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Trunk port to router/uplink (tagged for all VLANs)
/interface bridge port
add bridge=bridge interface=ether1 frame-types=admit-only-vlan-tagged
