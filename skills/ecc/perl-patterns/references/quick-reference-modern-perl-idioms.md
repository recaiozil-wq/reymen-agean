---
skill_id: d90decdfccb8
usage_count: 1
last_used: 2026-06-16
---
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