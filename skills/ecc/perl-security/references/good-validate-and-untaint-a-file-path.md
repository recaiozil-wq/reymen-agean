---
skill_id: 00ac712e2dad
usage_count: 1
last_used: 2026-06-16
---
# Good: Validate and untaint a file path
sub untaint_filename($input) {
    if ($input =~ m{^([a-zA-Z0-9._-]+)$}) {
        return $1;
    }
    die "Invalid filename: contains unsafe characters\n";
}