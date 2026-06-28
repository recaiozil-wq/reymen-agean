---
skill_id: f59b3045e60e
usage_count: 1
last_used: 2026-06-16
---
# Good: Encode for URL context
sub safe_url_param($value) {
    return uri_escape_utf8($value);
}