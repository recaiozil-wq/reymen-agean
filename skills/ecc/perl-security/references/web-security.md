---
skill_id: e00e1b12789e
usage_count: 1
last_used: 2026-06-16
---
## Web Security

### XSS Prevention

```perl
use v5.36;
use HTML::Entities qw(encode_entities);
use URI::Escape qw(uri_escape_utf8);