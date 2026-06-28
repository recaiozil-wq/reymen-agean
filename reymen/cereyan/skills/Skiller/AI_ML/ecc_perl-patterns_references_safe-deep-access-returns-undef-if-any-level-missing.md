---
name: ecc_perl-patterns_references_safe-deep-access-returns-undef-if-any-level-missing
description: Safe deep access (returns undef if any level missing)
title: "Ecc Perl Patterns References Safe Deep Access Returns Undef If Any Level Missing"
version: 1.0.0
---

| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** |  |
| **Nerede** | `AI_ML/ecc_perl-patterns_references_safe-deep-access-returns-undef-if-any-level-missing.md` |
| **Ne Zaman** |  |
| **Neden** |  |
| **Nasıl** |  |

# Safe deep access (returns undef if any level missing)
my $port = $config->{database}{port};           # 5432
my $missing = $config->{cache}{host};           # undef, no error
