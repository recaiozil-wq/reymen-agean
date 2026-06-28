---
skill_id: 1e8b815561cf
usage_count: 1
last_used: 2026-06-16
---
# DBIx::Class generates safe parameterized queries
my @users = $schema->resultset('User')->search({
    status => 'active',
    email  => { -like => '%@example.com' },
}, {
    order_by => { -asc => 'name' },
    rows     => 50,
});
```