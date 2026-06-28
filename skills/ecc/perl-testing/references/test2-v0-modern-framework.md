---
skill_id: ffb0350f07eb
usage_count: 1
last_used: 2026-06-16
---
## Test2::V0 Modern Framework

Test2::V0 is the modern replacement for Test::More — richer assertions, better diagnostics, and extensible.

### Why Test2?

- Superior deep comparison with hash/array builders
- Better diagnostic output on failures
- Subtests with cleaner scoping
- Extensible via Test2::Tools::* plugins
- Backward-compatible with Test::More tests

### Deep Comparison with Builders

```perl
use v5.36;
use Test2::V0;