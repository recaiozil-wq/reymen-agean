---
name: ecc_perl-testing_references_run-only-failing-tests-from-last-run
description: Run only failing tests from last run
title: "Ecc Perl Testing References Run Only Failing Tests From Last Run"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Run only failing tests from last run |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Run only failing tests from last run
prove -l --state=failed t/
