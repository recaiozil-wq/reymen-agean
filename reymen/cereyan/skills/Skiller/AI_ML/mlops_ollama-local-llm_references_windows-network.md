---
name: mlops_ollama-local-llm_references_windows-network
description: Windows network enumeration notes
title: "Mlops Ollama Local Llm References Windows Network"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Windows network enumeration notes |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Windows network enumeration notes

Use stdlib first. The first reliable implementation here was:

- IP via `socket.gethostbyname(socket.gethostname())`
- MAC via `uuid.getnode()`
- Cross-check with `ipconfig /all` and `getmac`
- ARP only for LAN peers, not local adapters

Avoid ad-hoc parsing of Windows console tables in generated scripts; it is fragile.
