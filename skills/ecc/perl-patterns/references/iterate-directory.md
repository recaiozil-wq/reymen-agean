---
skill_id: c5fc211a7687
usage_count: 1
last_used: 2026-06-16
---
# Iterate directory
for my $child (path('src')->children(qr/\.pl$/)) {
    say $child->basename;
}
```