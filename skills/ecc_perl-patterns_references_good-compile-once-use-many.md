---
name: ecc_perl-patterns_references_good-compile-once-use-many
description: "Good: Compile once, use many"
title: "Ecc Perl Patterns References Good Compile Once Use Many"
version: 1.0.0
---

| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** |  |
| **Nerede** | `AI_ML/ecc_perl-patterns_references_good-compile-once-use-many.md` |
| **Ne Zaman** |  |
| **Neden** |  |
| **Nasıl** |  |

# Good: Compile once, use many
my $email_re = qr/^[A-Za-z0-9._%+-]+\@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$/;

sub validate_emails(@emails) {
    return grep { $_ =~ $email_re } @emails;
}
```
