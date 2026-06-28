---
skill_id: 04557692a5f4
usage_count: 1
last_used: 2026-06-16
---
# 5. Global variables as configuration
our $TIMEOUT = 30;                       # Bad: mutable global
use constant TIMEOUT => 30;              # Better: constant