---
name: ecc_perl-patterns_references_cpanfile
description: cpanfile
title: "Ecc Perl Patterns References Cpanfile"
version: 1.0.0
---

| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** |  |
| **Nerede** | `AI_ML/ecc_perl-patterns_references_cpanfile.md` |
| **Ne Zaman** |  |
| **Neden** |  |
| **Nasıl** |  |

# cpanfile
requires 'Moo', '>= 2.005';
requires 'Path::Tiny';
requires 'JSON::MaybeXS';
requires 'Try::Tiny';

on test => sub {
    requires 'Test2::V0';
    requires 'Test::MockModule';
};
```
