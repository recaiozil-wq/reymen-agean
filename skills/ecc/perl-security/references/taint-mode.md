---
skill_id: 95bd0f86d762
usage_count: 1
last_used: 2026-06-16
---
## Taint Mode

Perl's taint mode (`-T`) tracks data from external sources and prevents it from being used in unsafe operations without explicit validation.

### Enabling Taint Mode

```perl
#!/usr/bin/perl -T
use v5.36;