---
name: ecc_java-coding-standards_references_streams-best-practices
description: Streams Best Practices
title: "Ecc Java Coding Standards References Streams Best Practices"
version: 1.0.0
---

| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** |  |
| **Nerede** | `AI_ML/ecc_java-coding-standards_references_streams-best-practices.md` |
| **Ne Zaman** |  |
| **Neden** |  |
| **Nasıl** |  |

## Streams Best Practices

```java
// PASS: Use streams for transformations, keep pipelines short
List<String> names = markets.stream()
    .map(Market::name)
    .filter(Objects::nonNull)
    .toList();

// FAIL: Avoid complex nested streams; prefer loops for clarity
```
