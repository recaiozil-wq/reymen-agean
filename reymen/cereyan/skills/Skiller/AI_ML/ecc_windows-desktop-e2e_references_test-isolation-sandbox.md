---
name: ecc_windows-desktop-e2e_references_test-isolation-sandbox
description: Test Isolation & Sandbox
title: "Ecc Windows Desktop E2E References Test Isolation Sandbox"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Test Isolation & Sandbox |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

## Test Isolation & Sandbox

Three tiers of isolation — use the lightest tier that satisfies your needs.

### Tier 1 — Filesystem Isolation (default, always use)

Each test gets its own `APPDATA` / `LOCALAPPDATA` / `TEMP` via `subprocess.Popen` and `Application.connect()`. pytest's `tmp_path` fixture handles cleanup automatically.

```python
