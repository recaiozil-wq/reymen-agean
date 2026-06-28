---
name: ecc_homelab-vlan-segmentation_references_best-practices
description: Best Practices
title: "Ecc Homelab Vlan Segmentation References Best Practices"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Best Practices |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

## Best Practices

- Start with 4 VLANs: Trusted, IoT, Servers, Guest — add more as needed
- Put Pi-hole in the Servers VLAN (192.168.30.x)
- Add a firewall rule allowing DNS (port 53) from all VLANs to the Pi-hole IP — before any RFC1918 block rule
- Test isolation after every rule change: from the IoT VLAN, try to ping a trusted device — it should fail
- Use a management VLAN for switch and AP web UIs and restrict access to the Trusted VLAN only
- Document your VLAN design in a table (VLAN ID, name, subnet, purpose)
