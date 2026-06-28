---
skill_id: 0abd5800c32c
usage_count: 1
last_used: 2026-06-16
---
# Multi-variable for loop (experimental in 5.36, stable in 5.40)
use feature 'for_list';
no warnings 'experimental::for_list';
for my ($key, $val) (%$config) {
    say "$key => $val";
}
```