---
skill_id: c0065bf89a81
usage_count: 1
last_used: 2026-06-16
---
## Quick Reference

| Task | Command / Pattern |
|---|---|
| Run all tests | `prove -lr t/` |
| Run one test verbose | `prove -lv t/unit/user.t` |
| Parallel test run | `prove -lr -j8 t/` |
| Coverage report | `cover -test && cover -report html` |
| Test equality | `is($got, $expected, 'label')` |
| Deep comparison | `is($got, hash { field k => 'v'; etc() }, 'label')` |
| Test exception | `like(dies { ... }, qr/msg/, 'label')` |
| Test no exception | `ok(lives { ... }, 'label')` |
| Mock a method | `Test::MockModule->new('Pkg')->mock(m => sub { ... })` |
| Skip tests | `SKIP: { skip 'reason', $count unless $cond; ... }` |
| TODO tests | `TODO: { local $TODO = 'reason'; ... }` |