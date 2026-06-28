---
name: ecc_perl-testing_references_combined-pattern
description: Combined pattern
title: "Ecc Perl Testing References Combined Pattern"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Combined pattern |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Combined pattern
subtest 'error handling' => sub {
    ok(lives { parse_config('valid.json') }, 'valid config parses');
    like(
        dies { parse_config('missing.json') },
        qr/Cannot open/,
        'missing file dies with message'
    );
};

done_testing;
```
