---
name: ecc_kubernetes-patterns_references_how-it-works
description: How It Works
title: "Ecc Kubernetes Patterns References How It Works"
version: 1.0.0
---

| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** |  |
| **Nerede** | `AI_ML/ecc_kubernetes-patterns_references_how-it-works.md` |
| **Ne Zaman** |  |
| **Neden** |  |
| **Nasıl** |  |

## How It Works

This skill provides **copy-pasteable, production-grade YAML patterns** and **kubectl debugging commands** organized by task:

1. **Deployment template** — A fully configured production `Deployment` with security context, rolling update strategy, all three probe types, resource limits, and environment injection from ConfigMap/Secret.
2. **Probes** — Decision table for startup vs liveness vs readiness, with correct `failureThreshold × periodSeconds` math.
3. **Services & Ingress** — ClusterIP, LoadBalancer, and TLS Ingress patterns with cert-manager annotations.
4. **ConfigMaps & Secrets** — `envFrom`, file-mount, and external secrets guidance.
5. **Resource management** — Requests vs limits rules of thumb by workload type (web API, JVM, worker, sidecar).
6. **RBAC** — Least-privilege ServiceAccount → Role → RoleBinding chain.
7. **HPA & PDB** — Autoscaling and node-drain safety configurations.
8. **Jobs & CronJobs** — One-off and scheduled workload patterns with correct `restartPolicy`.
9. **kubectl cheatsheet** — Logs, exec, rollback, port-forward, dry-run, and common error diagnosis commands.
10. **Anti-patterns & checklist** — What NOT to do, and a security/reliability/observability checklist.
