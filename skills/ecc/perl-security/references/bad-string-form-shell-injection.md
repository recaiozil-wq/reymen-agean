---
skill_id: 2c142aa213f3
usage_count: 1
last_used: 2026-06-16
---
# Bad: String form — shell injection!
sub bad_search($pattern) {
    system("grep -r '$pattern' /var/log/app/");  # If $pattern = "'; rm -rf / #"
}