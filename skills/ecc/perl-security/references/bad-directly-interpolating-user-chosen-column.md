---
skill_id: 6a530a5a5193
usage_count: 1
last_used: 2026-06-16
---
# Bad: Directly interpolating user-chosen column
sub bad_order($dbh, $column) {
    $dbh->prepare("SELECT * FROM users ORDER BY $column");  # SQLi!
}
```

### DBIx::Class (ORM Safety)

```perl
use v5.36;