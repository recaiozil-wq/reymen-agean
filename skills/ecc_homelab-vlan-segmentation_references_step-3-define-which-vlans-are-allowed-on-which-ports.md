---
name: ecc_homelab-vlan-segmentation_references_step-3-define-which-vlans-are-allowed-on-which-ports
description: "Step 3: Define which VLANs are allowed on which ports"
title: "Ecc Homelab Vlan Segmentation References Step 3 Define Which Vlans Are Allowed On Which Ports"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Step 3: Define which VLANs are allowed on which ports |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Step 3: Define which VLANs are allowed on which ports
/interface bridge vlan
add bridge=bridge tagged=ether1 untagged=ether2 vlan-ids=10
add bridge=bridge tagged=ether1 untagged=ether3 vlan-ids=20
