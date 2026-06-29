---
name: ecc_perl-patterns_references_hash-slices
description: Hash slices
title: "Ecc Perl Patterns References Hash Slices"
version: 1.0.0
---

| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** |  |
| **Nerede** | `AI_ML/ecc_perl-patterns_references_hash-slices.md` |
| **Ne Zaman** |  |
| **Neden** |  |
| **Nasıl** |  |

# Hash slices
my %subset;
@subset{qw(host port)} = @{$config->{database}}{qw(host port)};
