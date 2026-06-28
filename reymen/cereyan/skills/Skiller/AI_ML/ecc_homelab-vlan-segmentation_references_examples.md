---
name: ecc_homelab-vlan-segmentation_references_examples
description: Examples
title: "Ecc Homelab Vlan Segmentation References Examples"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Examples |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

## Examples

**Typical homelab with UniFi AP and managed switch:**

```
Scenario: 3-bedroom house, UniFi Dream Machine + UniFi 8-port switch + 2 APs

VLAN 10 — Trusted    192.168.10.0/24   MacBook, iPhones, iPad
VLAN 20 — IoT        192.168.20.0/24   Nest thermostat, Philips Hue, Ring doorbell, smart TVs
VLAN 30 — Servers    192.168.30.0/24   Synology NAS (192.168.30.10), Pi-hole (192.168.30.2)
VLAN 40 — Guest      192.168.40.0/24   Visitor Wi-Fi — internet only

SSID → VLAN mapping:
  "Home"      → VLAN 10 (WPA2, strong password, trusted devices only)
  "IoT"       → VLAN 20 (WPA2, separate password, printed on router for setup)
  "Guest"     → VLAN 40 (WPA2, simple password you can share freely)

Switch port behavior:
  Port 1  → trunk to router (tagged VLANs 10,20,30,40,99)
  Port 2  → trunk to APs (tagged VLANs 10,20,40; AP handles per-SSID tagging)
  Port 3  → access VLAN 30 (NAS — untagged, no VLAN awareness needed)
  Port 4  → access VLAN 30 (Pi-hole — untagged)
  Port 5–8 → access VLAN 10 (wired workstations)

Firewall rules applied (all rules add isolation, none remove existing protections):
  IoT → Trusted: BLOCK
  IoT → Servers: BLOCK except 192.168.30.2:53 (Pi-hole DNS allowed)
  IoT → Internet: ALLOW
  Guest → Local networks: BLOCK
  Guest → Internet: ALLOW
  Trusted → everywhere: ALLOW
```
