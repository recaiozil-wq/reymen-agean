---
skill_id: 682972cbcbfd
usage_count: 1
last_used: 2026-06-16
---
# Validate path stays within allowed directory
sub safe_path($base_dir, $user_path) {
    my $real = realpath(File::Spec->catfile($base_dir, $user_path))
        // die "Path does not exist\n";
    my $base_real = realpath($base_dir)
        // die "Base dir does not exist\n";
    die "Path traversal blocked\n" unless $real =~ /^\Q$base_real\E(?:\/|\z)/;
    return $real;
}
```

Use `File::Temp` for temporary files (`tempfile(UNLINK => 1)`) and `flock(LOCK_EX)` to prevent race conditions.