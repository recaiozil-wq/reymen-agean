---
name: ecc_perl-patterns_references_bad-two-arg-open-shell-injection-risk-see-perl-security
description: "Bad: Two-arg open (shell injection risk, see perl-security)"
title: "Ecc Perl Patterns References Bad Two Arg Open Shell Injection Risk See Perl Security"
version: 1.0.0
---

| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** |  |
| **Nerede** | `AI_ML/ecc_perl-patterns_references_bad-two-arg-open-shell-injection-risk-see-perl-security.md` |
| **Ne Zaman** |  |
| **Neden** |  |
| **Nasıl** |  |

# Bad: Two-arg open (shell injection risk, see perl-security)
open FH, $path;            # NEVER do this
open FH, "< $path";        # Still bad — user data in mode string
```

### Path::Tiny for File Operations

```perl
use v5.36;
use Path::Tiny;

my $file = path('config', 'app.json');
my $content = $file->slurp_utf8;
$file->spew_utf8($new_content);
