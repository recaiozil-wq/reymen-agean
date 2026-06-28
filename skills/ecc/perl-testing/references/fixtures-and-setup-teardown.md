---
skill_id: 790618051cf2
usage_count: 1
last_used: 2026-06-16
---
## Fixtures and Setup/Teardown

### Subtest Isolation

```perl
use v5.36;
use Test2::V0;
use File::Temp qw(tempdir);
use Path::Tiny;

subtest 'file processing' => sub {