---
skill_id: f44d62ae711a
usage_count: 1
last_used: 2026-06-16
---
# Good: Slurpy parameter for variable args
sub log_message($level, @details) {
    say "[$level] " . join(' ', @details);
}