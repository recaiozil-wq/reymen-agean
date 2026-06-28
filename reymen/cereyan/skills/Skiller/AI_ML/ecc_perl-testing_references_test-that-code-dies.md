---
name: ecc_perl-testing_references_test-that-code-dies
description: Test that code dies
title: "Ecc Perl Testing References Test That Code Dies"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Test that code dies |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Test that code dies
like(
    dies { divide(10, 0) },
    qr/Division by zero/,
    'dies on division by zero'
);
