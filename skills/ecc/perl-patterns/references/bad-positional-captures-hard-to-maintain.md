---
skill_id: faa78d58e7b2
usage_count: 1
last_used: 2026-06-16
---
# Bad: Positional captures (hard to maintain)
if ($line =~ /^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\s+\[(\w+)\]\s+(.+)$/) {
    say "Time: $1, Level: $2";
}
```

### Precompiled Patterns

```perl
use v5.36;