---
skill_id: 09b828bda630
usage_count: 1
last_used: 2026-06-16
---
# Sanitize PATH early (required in taint mode)
$ENV{PATH} = '/usr/local/bin:/usr/bin:/bin';
delete @ENV{qw(IFS CDPATH ENV BASH_ENV)};
```

### Untainting Pattern

```perl
use v5.36;