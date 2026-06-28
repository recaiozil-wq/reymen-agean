---
skill_id: aa87fefc65d7
usage_count: 1
last_used: 2026-06-16
---
# Good: Allowlist — define exactly what's permitted
sub validate_sort_field($field) {
    my %allowed = map { $_ => 1 } qw(name email created_at updated_at);
    die "Invalid sort field: $field\n" unless $allowed{$field};
    return $field;
}