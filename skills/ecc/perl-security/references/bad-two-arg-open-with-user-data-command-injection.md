---
skill_id: 1c4166ef39d3
usage_count: 1
last_used: 2026-06-16
---
# Bad: Two-arg open with user data (command injection)
sub bad_read($path) {
    open my $fh, $path;        # If $path = "|rm -rf /", runs command!
    open my $fh, "< $path";   # Shell metacharacter injection
}
```

### TOCTOU Prevention and Path Traversal

```perl
use v5.36;
use Fcntl qw(:DEFAULT :flock);
use File::Spec;
use Cwd qw(realpath);