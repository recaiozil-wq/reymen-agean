---
name: ecc_kubernetes-patterns_references_container-security-context
description: Container security context
title: "Ecc Kubernetes Patterns References Container Security Context"
version: 1.0.0
---

| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** |  |
| **Nerede** | `AI_ML/ecc_kubernetes-patterns_references_container-security-context.md` |
| **Ne Zaman** |  |
| **Neden** |  |
| **Nasıl** |  |

# Container security context
          securityContext:
            allowPrivilegeEscalation: false
            readOnlyRootFilesystem: true
            capabilities:
              drop:
                - ALL
