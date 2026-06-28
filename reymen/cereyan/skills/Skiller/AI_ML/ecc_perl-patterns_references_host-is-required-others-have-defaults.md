---
name: ecc_perl-patterns_references_host-is-required-others-have-defaults
description: $host is required, others have defaults
title: "Ecc Perl Patterns References Host Is Required Others Have Defaults"
version: 1.0.0
---

| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** |  |
| **Nerede** | `AI_ML/ecc_perl-patterns_references_host-is-required-others-have-defaults.md` |
| **Ne Zaman** |  |
| **Neden** |  |
| **Nasıl** |  |

# $host is required, others have defaults
    return DBI->connect("dbi:Pg:host=$host;port=$port", undef, undef, {
        RaiseError => 1,
        PrintError => 0,
    });
}
