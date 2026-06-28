---
skill_id: d1892d85020b
usage_count: 1
last_used: 2026-06-16
---
## Mocking

### Test::MockModule

```perl
use v5.36;
use Test2::V0;
use Test::MockModule;

subtest 'mock external API' => sub {
    my $mock = Test::MockModule->new('MyApp::API');