---
name: ecc_perl-patterns_references_bad-positional-captures-hard-to-maintain
description: "Bad: Positional captures (hard to maintain)"
title: "Ecc Perl Patterns References Bad Positional Captures Hard To Maintain"
version: 1.0.0
---

| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** |  |
| **Nerede** | `AI_ML/ecc_perl-patterns_references_bad-positional-captures-hard-to-maintain.md` |
| **Ne Zaman** |  |
| **Neden** |  |
| **Nasıl** |  |

# Bad: Positional captures (hard to maintain)
if ($line =~ /^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\s+\[(\w+)\]\s+(.+)$/) {
    say "Time: $1, Level: $2";
}
```

### Precompiled Patterns

```perl
use v5.36;
