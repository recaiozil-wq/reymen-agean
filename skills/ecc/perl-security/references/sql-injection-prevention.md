---
skill_id: 8fe0e2d04d80
usage_count: 1
last_used: 2026-06-16
---
## SQL Injection Prevention

### DBI Placeholders

```perl
use v5.36;
use DBI;

my $dbh = DBI->connect($dsn, $user, $pass, {
    RaiseError => 1,
    PrintError => 0,
    AutoCommit => 1,
});