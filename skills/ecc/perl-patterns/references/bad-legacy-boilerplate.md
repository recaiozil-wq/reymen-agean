---
skill_id: a9bc26ebd790
usage_count: 1
last_used: 2026-06-16
---
# Bad: Legacy boilerplate
use strict;
use warnings;
use feature 'say', 'signatures';
no warnings 'experimental::signatures';

sub greet {
    my ($name) = @_;
    say "Hello, $name!";
}
```

### 2. Subroutine Signatures

Use signatures for clarity and automatic arity checking.

```perl
use v5.36;