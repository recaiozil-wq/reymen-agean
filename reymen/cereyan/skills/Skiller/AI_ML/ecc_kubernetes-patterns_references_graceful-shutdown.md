---
name: ecc_kubernetes-patterns_references_graceful-shutdown
description: Graceful shutdown
title: "Ecc Kubernetes Patterns References Graceful Shutdown"
version: 1.0.0
---

| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** |  |
| **Nerede** | `AI_ML/ecc_kubernetes-patterns_references_graceful-shutdown.md` |
| **Ne Zaman** |  |
| **Neden** |  |
| **Nasıl** |  |

# Graceful shutdown
      terminationGracePeriodSeconds: 30

      containers:
        - name: my-app
          image: ghcr.io/org/my-app:1.0.0   # Never use :latest
          imagePullPolicy: IfNotPresent

          ports:
            - containerPort: 8080
              protocol: TCP
