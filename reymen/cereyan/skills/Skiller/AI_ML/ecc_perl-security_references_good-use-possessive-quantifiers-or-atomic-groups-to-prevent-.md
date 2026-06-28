---
name: ecc_perl-security_references_good-use-possessive-quantifiers-or-atomic-groups-to-prevent-
description: "Good: Use possessive quantifiers or atomic groups to prevent backtracking"
title: "Ecc Perl Security References Good Use Possessive Quantifiers Or Atomic Groups To Prevent "
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Good: Use possessive quantifiers or atomic groups to prevent backtracking |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Good: Use possessive quantifiers or atomic groups to prevent backtracking
my $safe_re = qr/^[a-zA-Z]++$/;             # Possessive (5.10+)
my $safe_re2 = qr/^(?>a+)$/;                # Atomic group
