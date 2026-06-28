---
skill_id: 77dc70aa696c
usage_count: 1
last_used: 2026-06-16
---
# If $email = "' OR 1=1 --", returns all users
    $sth->execute;
    return $sth->fetchrow_hashref;
}
```

### Dynamic Column Allowlists

```perl
use v5.36;