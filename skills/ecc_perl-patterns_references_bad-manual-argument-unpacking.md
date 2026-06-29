---
name: ecc_perl-patterns_references_bad-manual-argument-unpacking
description: "Bad: Manual argument unpacking"
title: "Ecc Perl Patterns References Bad Manual Argument Unpacking"
version: 1.0.0
---

| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** |  |
| **Nerede** | `AI_ML/ecc_perl-patterns_references_bad-manual-argument-unpacking.md` |
| **Ne Zaman** |  |
| **Neden** |  |
| **Nasıl** |  |

# Bad: Manual argument unpacking
sub connect_db {
    my ($host, $port, $timeout) = @_;
    $port    //= 5432;
    $timeout //= 30;
