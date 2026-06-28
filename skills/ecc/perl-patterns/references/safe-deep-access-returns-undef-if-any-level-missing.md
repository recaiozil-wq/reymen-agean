---
skill_id: 2d67a2c414ef
usage_count: 1
last_used: 2026-06-16
---
# Safe deep access (returns undef if any level missing)
my $port = $config->{database}{port};           # 5432
my $missing = $config->{cache}{host};           # undef, no error