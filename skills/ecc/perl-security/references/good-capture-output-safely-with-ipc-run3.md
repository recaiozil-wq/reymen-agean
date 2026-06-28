---
skill_id: 9eba1f81735c
usage_count: 1
last_used: 2026-06-16
---
# Good: Capture output safely with IPC::Run3
use IPC::Run3;
sub capture_output(@cmd) {
    my ($stdout, $stderr);
    run3(\@cmd, \undef, \$stdout, \$stderr);
    if ($?) {
        die "Command failed (exit $?): $stderr\n";
    }
    return $stdout;
}