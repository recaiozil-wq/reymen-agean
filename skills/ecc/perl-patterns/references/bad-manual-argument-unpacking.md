---
skill_id: 3c7228140b97
usage_count: 1
last_used: 2026-06-16
---
# Bad: Manual argument unpacking
sub connect_db {
    my ($host, $port, $timeout) = @_;
    $port    //= 5432;
    $timeout //= 30;