---
name: ecc_homelab-vlan-segmentation_references_step-6-dhcp-pools-and-servers
description: "Step 6: DHCP pools and servers"
title: "Ecc Homelab Vlan Segmentation References Step 6 Dhcp Pools And Servers"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Step 6: DHCP pools and servers |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Step 6: DHCP pools and servers
/ip pool
add name=pool-trusted ranges=192.168.10.100-192.168.10.254
add name=pool-iot ranges=192.168.20.100-192.168.20.254

/ip dhcp-server
add interface=vlan10 address-pool=pool-trusted name=dhcp-trusted
add interface=vlan20 address-pool=pool-iot name=dhcp-iot

/ip dhcp-server network
add address=192.168.10.0/24 gateway=192.168.10.1
add address=192.168.20.0/24 gateway=192.168.20.1
