---
name: ecc_kubernetes-patterns_references_probes-liveness-readiness-startup
description: Probes — Liveness, Readiness, Startup
title: "Ecc Kubernetes Patterns References Probes Liveness Readiness Startup"
version: 1.0.0
---

| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** |  |
| **Nerede** | `AI_ML/ecc_kubernetes-patterns_references_probes-liveness-readiness-startup.md` |
| **Ne Zaman** |  |
| **Neden** |  |
| **Nasıl** |  |

## Probes — Liveness, Readiness, Startup

Understanding when to use each probe is critical:

| Probe | Failure Action | Use For |
|-------|---------------|---------|
| `startupProbe` | Kills container if slow to start | Slow-starting apps (JVM, Python) |
| `livenessProbe` | Restarts container | Deadlock / hung process detection |
| `readinessProbe` | Removes from Service endpoints | Temporary unavailability (DB reconnect) |

```yaml
