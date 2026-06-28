---
skill_id: dda54106bb1d
usage_count: 1
last_used: 2026-06-16
---
# Bad: Backticks with interpolation
my $output = `ls $user_dir`;   # Shell injection risk
```

Also use `Capture::Tiny` for capturing stdout/stderr from external commands safely.