---
name: ecc_perl-patterns_references_4-disabling-strict-refs
description: 4.
title: "Ecc Perl Patterns References 4 Disabling Strict Refs"
version: 1.0.0
---

| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** |  |
| **Nerede** | `AI_ML/ecc_perl-patterns_references_4-disabling-strict-refs.md` |
| **Ne Zaman** |  |
| **Neden** |  |
| **Nasıl** |  |

# 4. Disabling strict refs
no strict 'refs';                        # Almost always wrong
${"My::Package::$var"} = $value;         # Use a hash instead
