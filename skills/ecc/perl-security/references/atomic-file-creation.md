---
skill_id: 670f607a5f89
usage_count: 1
last_used: 2026-06-16
---
# Atomic file creation
sub create_file_safe($path) {
    sysopen(my $fh, $path, O_WRONLY | O_CREAT | O_EXCL, 0600)
        or die "Cannot create '$path': $!\n";
    return $fh;
}