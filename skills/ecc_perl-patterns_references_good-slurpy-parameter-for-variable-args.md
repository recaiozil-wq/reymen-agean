---
name: ecc_perl-patterns_references_good-slurpy-parameter-for-variable-args
description: "Good: Slurpy parameter for variable args"
title: "Ecc Perl Patterns References Good Slurpy Parameter For Variable Args"
version: 1.0.0
---

| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** |  |
| **Nerede** | `AI_ML/ecc_perl-patterns_references_good-slurpy-parameter-for-variable-args.md` |
| **Ne Zaman** |  |
| **Neden** |  |
| **Nasıl** |  |

# Good: Slurpy parameter for variable args
sub log_message($level, @details) {
    say "[$level] " . join(' ', @details);
}
