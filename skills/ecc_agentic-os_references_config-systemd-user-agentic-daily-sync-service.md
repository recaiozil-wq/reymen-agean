---
name: ecc_agentic-os_references_config-systemd-user-agentic-daily-sync-service
description: ~/.config/systemd/user/agentic-daily-sync.service
title: "Ecc Agentic Os References Config Systemd User Agentic Daily Sync Service"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | ~/.config/systemd/user/agentic-daily-sync.service |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# ~/.config/systemd/user/agentic-daily-sync.service
[Unit]
Description=Agentic OS Daily Sync

[Service]
Type=oneshot
ExecStart=/usr/local/bin/claude --cwd /path/to/project --command /daily-sync
```

```ini
