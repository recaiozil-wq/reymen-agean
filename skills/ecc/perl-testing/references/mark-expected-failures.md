---
skill_id: 7e8407f3d0b1
usage_count: 1
last_used: 2026-06-16
---
# Mark expected failures
TODO: {
    local $TODO = 'Caching not yet implemented';
    is($cache->get('key'), 'value', 'cache returns value');
}

done_testing;
```