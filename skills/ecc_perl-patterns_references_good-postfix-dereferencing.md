---
name: ecc_perl-patterns_references_good-postfix-dereferencing
description: "Good: Postfix dereferencing"
title: "Ecc Perl Patterns References Good Postfix Dereferencing"
version: 1.0.0
---

| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** |  |
| **Nerede** | `AI_ML/ecc_perl-patterns_references_good-postfix-dereferencing.md` |
| **Ne Zaman** |  |
| **Neden** |  |
| **Nasıl** |  |

# Good: Postfix dereferencing
my @users = $data->{users}->@*;
my @roles = $data->{users}[0]{roles}->@*;
my %first = $data->{users}[0]->%*;
