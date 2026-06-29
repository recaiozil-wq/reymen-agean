---
name: ecc_perl-patterns_references_module-organization
description: Module Organization
title: "Ecc Perl Patterns References Module Organization"
version: 1.0.0
---

| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** |  |
| **Nerede** | `AI_ML/ecc_perl-patterns_references_module-organization.md` |
| **Ne Zaman** |  |
| **Neden** |  |
| **Nasıl** |  |

## Module Organization

### Standard Project Layout

```text
MyApp/
├── lib/
│   └── MyApp/
│       ├── App.pm           # Main module
│       ├── Config.pm        # Configuration
│       ├── DB.pm            # Database layer
│       └── Util.pm          # Utilities
├── bin/
│   └── myapp                # Entry-point script
├── t/
│   ├── 00-load.t            # Compilation tests
│   ├── unit/                # Unit tests
│   └── integration/         # Integration tests
├── cpanfile                 # Dependencies
├── Makefile.PL              # Build system
└── .perlcriticrc            # Linting config
```

### Exporter Patterns

```perl
package MyApp::Util;
use v5.36;
use Exporter 'import';

our @EXPORT_OK   = qw(trim);
our %EXPORT_TAGS = (all => \@EXPORT_OK);

sub trim($str) { $str =~ s/^\s+|\s+$//gr }

1;
```
