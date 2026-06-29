---
name: ecc_uncloud_references_common-workflows
description: Common Workflows
title: "Ecc Uncloud References Common Workflows"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Common Workflows |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

## Common Workflows

**Deploy from source:**
```bash
uc deploy                          # Build + push + deploy
uc build --push && uc deploy --no-build   # Separate steps
```

**Inspect a service:**
```bash
uc inspect web
uc logs -f web
uc logs --since 1h web
uc exec web                        # Opens shell
uc exec web /bin/sh -c "env"       # Run specific command
```

**Zero-downtime deploys** happen automatically; Uncloud waits for health checks before terminating old containers.

**Force recreate:**
```bash
uc deploy --recreate
```
