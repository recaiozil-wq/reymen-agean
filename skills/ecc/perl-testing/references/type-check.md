---
skill_id: d40121290890
usage_count: 1
last_used: 2026-06-16
---
# Type check
isa_ok($obj, 'MyApp::User');
can_ok($obj, 'save', 'delete');

done_testing;
```

### SKIP and TODO

```perl
use v5.36;
use Test::More;