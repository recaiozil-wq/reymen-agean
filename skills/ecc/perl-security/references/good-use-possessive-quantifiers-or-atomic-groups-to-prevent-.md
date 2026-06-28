---
skill_id: e84121fcca61
usage_count: 1
last_used: 2026-06-16
---
# Good: Use possessive quantifiers or atomic groups to prevent backtracking
my $safe_re = qr/^[a-zA-Z]++$/;             # Possessive (5.10+)
my $safe_re2 = qr/^(?>a+)$/;                # Atomic group