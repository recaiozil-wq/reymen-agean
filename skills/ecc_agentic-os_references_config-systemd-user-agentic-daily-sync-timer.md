---
name: ecc_agentic-os_references_config-systemd-user-agentic-daily-sync-timer
description: ~/.config/systemd/user/agentic-daily-sync.timer
title: "Ecc Agentic Os References Config Systemd User Agentic Daily Sync Timer"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | ~/.config/systemd/user/agentic-daily-sync.timer |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# ~/.config/systemd/user/agentic-daily-sync.timer
[Unit]
Description=Run daily sync every morning

[Timer]
OnCalendar=*-*-* 8:00:00
Persistent=true

[Install]
WantedBy=timers.target
```

### Cross-Platform: pm2

```bash
