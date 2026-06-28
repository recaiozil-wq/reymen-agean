---
name: ecc_quarkus-verification_references_run-basic-smoke-tests
description: Run basic smoke tests
title: "Ecc Quarkus Verification References Run Basic Smoke Tests"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Run basic smoke tests |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Run basic smoke tests
curl http://localhost:8080/q/health/live
curl http://localhost:8080/q/health/ready
```

### Native Image Troubleshooting

Common issues:
- **Reflection**: Add reflection config for dynamic classes
- **Resources**: Include resources with `quarkus.native.resources.includes`
- **JNI**: Register JNI classes if using native libraries

Example reflection config:
```java
@RegisterForReflection(targets = {MyDynamicClass.class})
public class ReflectionConfiguration {}
```
