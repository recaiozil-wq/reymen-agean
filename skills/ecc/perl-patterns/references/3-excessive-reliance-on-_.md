---
skill_id: e44dd8b6ef4f
usage_count: 1
last_used: 2026-06-16
---
# 3. Excessive reliance on $_
map { process($_) } grep { validate($_) } @items;  # Hard to follow
my @valid = grep { validate($_) } @items;           # Better: break it up
my @results = map { process($_) } @valid;