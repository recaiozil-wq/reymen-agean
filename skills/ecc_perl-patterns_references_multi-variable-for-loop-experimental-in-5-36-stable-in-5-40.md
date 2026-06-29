---
name: ecc_perl-patterns_references_multi-variable-for-loop-experimental-in-5-36-stable-in-5-40
description: Multi-variable for loop (experimental in 5.36, stable in 5.40)
title: "Ecc Perl Patterns References Multi Variable For Loop Experimental In 5 36 Stable In 5 40"
version: 1.0.0
---

| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** |  |
| **Nerede** | `AI_ML/ecc_perl-patterns_references_multi-variable-for-loop-experimental-in-5-36-stable-in-5-40.md` |
| **Ne Zaman** |  |
| **Neden** |  |
| **Nasıl** |  |

# Multi-variable for loop (experimental in 5.36, stable in 5.40)
use feature 'for_list';
no warnings 'experimental::for_list';
for my ($key, $val) (%$config) {
    say "$key => $val";
}
```
