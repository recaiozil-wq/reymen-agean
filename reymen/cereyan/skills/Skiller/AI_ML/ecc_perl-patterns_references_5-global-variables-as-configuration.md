---
name: ecc_perl-patterns_references_5-global-variables-as-configuration
description: 5.
title: "Ecc Perl Patterns References 5 Global Variables As Configuration"
version: 1.0.0
---

| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** |  |
| **Nerede** | `AI_ML/ecc_perl-patterns_references_5-global-variables-as-configuration.md` |
| **Ne Zaman** |  |
| **Neden** |  |
| **Nasıl** |  |

# 5. Global variables as configuration
our $TIMEOUT = 30;                       # Bad: mutable global
use constant TIMEOUT => 30;              # Better: constant
