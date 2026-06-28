---
skill_id: 99a2187657f4
usage_count: 1
last_used: 2026-06-16
---
# Combined pattern
subtest 'error handling' => sub {
    ok(lives { parse_config('valid.json') }, 'valid config parses');
    like(
        dies { parse_config('missing.json') },
        qr/Cannot open/,
        'missing file dies with message'
    );
};

done_testing;
```