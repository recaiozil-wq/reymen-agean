---
skill_id: 5ad4e98c3228
usage_count: 1
last_used: 2026-06-16
---
# cpanfile
requires 'Moo', '>= 2.005';
requires 'Path::Tiny';
requires 'JSON::MaybeXS';
requires 'Try::Tiny';

on test => sub {
    requires 'Test2::V0';
    requires 'Test::MockModule';
};
```