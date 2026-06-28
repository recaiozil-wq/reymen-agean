---
name: ecc_perl-security_references_bad-backticks-with-interpolation
description: "Bad: Backticks with interpolation"
title: "Ecc Perl Security References Bad Backticks With Interpolation"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Bad: Backticks with interpolation |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Bad: Backticks with interpolation
my $output = `ls $user_dir`;   # Shell injection risk
```

Also use `Capture::Tiny` for capturing stdout/stderr from external commands safely.
