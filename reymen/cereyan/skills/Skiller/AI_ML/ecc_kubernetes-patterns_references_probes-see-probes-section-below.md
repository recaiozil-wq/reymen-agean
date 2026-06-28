---
name: ecc_kubernetes-patterns_references_probes-see-probes-section-below
description: Probes (see Probes section below)
title: "Ecc Kubernetes Patterns References Probes See Probes Section Below"
version: 1.0.0
---

| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** |  |
| **Nerede** | `AI_ML/ecc_kubernetes-patterns_references_probes-see-probes-section-below.md` |
| **Ne Zaman** |  |
| **Neden** |  |
| **Nasıl** |  |

# Probes (see Probes section below)
          startupProbe:
            httpGet:
              path: /health
              port: 8080
            failureThreshold: 30
            periodSeconds: 5
          livenessProbe:
            httpGet:
              path: /health
              port: 8080
            initialDelaySeconds: 0
            periodSeconds: 30
            failureThreshold: 3
          readinessProbe:
            httpGet:
              path: /ready
              port: 8080
            initialDelaySeconds: 5
            periodSeconds: 10
            failureThreshold: 2
