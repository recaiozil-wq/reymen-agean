---
name: ecc_perl-patterns_references_bad-circumfix-dereferencing-harder-to-read-in-chains
description: "Bad: Circumfix dereferencing (harder to read in chains)"
title: "Ecc Perl Patterns References Bad Circumfix Dereferencing Harder To Read In Chains"
version: 1.0.0
---

| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** |  |
| **Nerede** | `AI_ML/ecc_perl-patterns_references_bad-circumfix-dereferencing-harder-to-read-in-chains.md` |
| **Ne Zaman** |  |
| **Neden** |  |
| **Nasıl** |  |

# Bad: Circumfix dereferencing (harder to read in chains)
my @users = @{ $data->{users} };
my @roles = @{ $data->{users}[0]{roles} };
```

### 5. The `isa` Operator (5.32+)

Infix type-check — replaces `blessed($o) && $o->isa('X')`.

```perl
use v5.36;
if ($obj isa 'My::Class') { $obj->do_something }
```
