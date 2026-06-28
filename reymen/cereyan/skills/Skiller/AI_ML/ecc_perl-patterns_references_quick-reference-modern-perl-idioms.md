---
name: ecc_perl-patterns_references_quick-reference-modern-perl-idioms
description: "Quick Reference: Modern Perl Idioms"
title: "Ecc Perl Patterns References Quick Reference Modern Perl Idioms"
version: 1.0.0
---

| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** |  |
| **Nerede** | `AI_ML/ecc_perl-patterns_references_quick-reference-modern-perl-idioms.md` |
| **Ne Zaman** |  |
| **Neden** |  |
| **Nasıl** |  |

## Quick Reference: Modern Perl Idioms

| Legacy Pattern | Modern Replacement |
|---|---|
| `use strict; use warnings;` | `use v5.36;` |
| `my ($x, $y) = @_;` | `sub foo($x, $y) { ... }` |
| `@{ $ref }` | `$ref->@*` |
| `%{ $ref }` | `$ref->%*` |
| `open FH, "< $file"` | `open my $fh, '<:encoding(UTF-8)', $file` |
| `blessed hashref` | `Moo` class with types |
| `$1, $2, $3` | `$+{name}` (named captures) |
| `eval { }; if ($@)` | `Try::Tiny` or native `try/catch` (5.40+) |
| `BEGIN { require Exporter; }` | `use Exporter 'import';` |
| Manual file ops | `Path::Tiny` |
| `blessed($o) && $o->isa('X')` | `$o isa 'X'` (5.32+) |
| `builtin::true / false` | `use builtin 'true', 'false';` (5.36+, experimental) |
