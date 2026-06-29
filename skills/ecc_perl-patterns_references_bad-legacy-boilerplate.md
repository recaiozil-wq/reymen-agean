---
name: ecc_perl-patterns_references_bad-legacy-boilerplate
description: "Bad: Legacy boilerplate"
title: "Ecc Perl Patterns References Bad Legacy Boilerplate"
version: 1.0.0
---

| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** |  |
| **Nerede** | `AI_ML/ecc_perl-patterns_references_bad-legacy-boilerplate.md` |
| **Ne Zaman** |  |
| **Neden** |  |
| **Nasıl** |  |

# Bad: Legacy boilerplate
use strict;
use warnings;
use feature 'say', 'signatures';
no warnings 'experimental::signatures';

sub greet {
    my ($name) = @_;
    say "Hello, $name!";
}
```

### 2. Subroutine Signatures

Use signatures for clarity and automatic arity checking.

```perl
use v5.36;
