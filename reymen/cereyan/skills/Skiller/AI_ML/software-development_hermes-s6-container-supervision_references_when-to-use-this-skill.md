---
name: software-development_hermes-s6-container-supervision_references_when-to-use-this-skill
description: When to use this skill
title: "Software Development Hermes S6 Container Supervision References When To Use This Skill"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | When to use this skill |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

## When to use this skill

Load this skill when you're working on:
- Adding or removing a static service in the Hermes Docker image (something that should be supervised at every container start, like the dashboard)
- Diagnosing why a per-profile gateway isn't starting, restarting, or surviving `docker restart`
- Understanding why the container's CMD is `/opt/hermes/docker/main-wrapper.sh` and how leading-dash args reach the user's program
- Modifying `cont-init.d` boot scripts (UID remap, volume seeding, profile reconciliation)
- Changing the rendered run-script for per-profile gateways (Phase 4)

If you're just running the Hermes Agent and want to use Docker, see `website/docs/user-guide/docker.md` instead.
