---
name: ecc_homelab-vlan-segmentation_references_additional-exceptions-for-iot-devices-that-need-specific-loc
description: "Additional exceptions for IoT devices that need specific local services:"
title: "Ecc Homelab Vlan Segmentation References Additional Exceptions For Iot Devices That Need Specific Loc"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Additional exceptions for IoT devices that need specific local services: |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Additional exceptions for IoT devices that need specific local services:
  Insert before Rule 2 (the RFC1918 block):
    Protocol: TCP
    Source: IoT net
    Destination: 192.168.30.x port 8123  ← Home Assistant
    Action: Allow
```
