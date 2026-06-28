---
name: ecc_perl-patterns_references_iterate-directory
description: Iterate directory
title: "Ecc Perl Patterns References Iterate Directory"
version: 1.0.0
---

| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** |  |
| **Nerede** | `AI_ML/ecc_perl-patterns_references_iterate-directory.md` |
| **Ne Zaman** |  |
| **Neden** |  |
| **Nasıl** |  |

# Iterate directory
for my $child (path('src')->children(qr/\.pl$/)) {
    say $child->basename;
}
```
