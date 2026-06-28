---
skill_id: e5113bf45f1c
usage_count: 1
last_used: 2026-06-16
---
# Bad: Overly permissive untainting (defeats the purpose)
sub bad_untaint($input) {
    $input =~ /^(.*)$/s;
    return $1;  # Accepts ANYTHING — pointless
}
```