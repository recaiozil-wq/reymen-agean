---
skill_id: 64c1b0e98421
usage_count: 1
last_used: 2026-06-16
---
# Good: List form — no shell interpolation
sub run_command(@cmd) {
    system(@cmd) == 0
        or die "Command failed: @cmd\n";
}

run_command('grep', '-r', $user_pattern, '/var/log/app/');