---
skill_id: 5e44abc88352
usage_count: 1
last_used: 2026-06-16
---
# Good: Validate and untaint with a specific regex
sub untaint_username($input) {
    if ($input =~ /^([a-zA-Z0-9_]{3,30})$/) {
        return $1;  # $1 is untainted
    }
    die "Invalid username: must be 3-30 alphanumeric characters\n";
}