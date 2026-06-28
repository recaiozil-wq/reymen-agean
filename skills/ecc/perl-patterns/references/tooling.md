---
skill_id: f7c5c7e78ad9
usage_count: 1
last_used: 2026-06-16
---
## Tooling

### perltidy Configuration (.perltidyrc)

```text
-i=4        # 4-space indent
-l=100      # 100-char line length
-ci=4       # continuation indent
-ce         # cuddled else
-bar        # opening brace on same line
-nolq       # don't outdent long quoted strings
```

### perlcritic Configuration (.perlcriticrc)

```ini
severity = 3
theme = core + pbp + security

[InputOutput::RequireCheckedSyscalls]
functions = :builtins
exclude_functions = say print

[Subroutines::ProhibitExplicitReturnUndef]
severity = 4

[ValuesAndExpressions::ProhibitMagicNumbers]
allowed_values = 0 1 2 -1
```

### Dependency Management (cpanfile + carton)

```bash
cpanm App::cpanminus Carton   # Install tools
carton install                 # Install deps from cpanfile
carton exec -- perl bin/myapp  # Run with local deps
```

```perl