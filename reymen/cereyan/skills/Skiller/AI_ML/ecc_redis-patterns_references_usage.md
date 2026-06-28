---
name: ecc_redis-patterns_references_usage
description: Usage
title: "Ecc Redis Patterns References Usage"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Usage |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Usage
token = acquire_lock("order:payment:123")
if token:
    try:
        process_payment()
    finally:
        release_lock("order:payment:123", token)
```

> For multi-node setups use the `redlock-py` library which implements the full Redlock algorithm.
