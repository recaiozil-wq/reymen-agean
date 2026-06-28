---
name: ecc_homelab-vlan-segmentation_references_step-1-create-a-bridge-with-vlan-filtering-enabled
description: "Step 1: Create a bridge with VLAN filtering enabled"
title: "Ecc Homelab Vlan Segmentation References Step 1 Create A Bridge With Vlan Filtering Enabled"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Step 1: Create a bridge with VLAN filtering enabled |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Step 1: Create a bridge with VLAN filtering enabled
/interface bridge
add name=bridge vlan-filtering=yes
