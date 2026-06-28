---
name: ecc_perl-patterns_references_2-indirect-object-syntax-ambiguous-parsing
description: 2.
title: "Ecc Perl Patterns References 2 Indirect Object Syntax Ambiguous Parsing"
version: 1.0.0
---

| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** |  |
| **Nerede** | `AI_ML/ecc_perl-patterns_references_2-indirect-object-syntax-ambiguous-parsing.md` |
| **Ne Zaman** |  |
| **Neden** |  |
| **Nasıl** |  |

# 2. Indirect object syntax (ambiguous parsing)
my $obj = new Foo(bar => 1);            # Bad
my $obj = Foo->new(bar => 1);           # Good
