---
name: ecc_perl-testing_references_tap-output-for-ci
description: TAP output for CI
title: "Ecc Perl Testing References Tap Output For Ci"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | TAP output for CI |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# TAP output for CI
prove -l --formatter TAP::Formatter::JUnit t/ > results.xml
```

### .proverc Configuration

```text
-l
--color
--timer
-r
-j4
--state=save
```
