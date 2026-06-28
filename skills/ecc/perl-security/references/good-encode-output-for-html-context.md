---
skill_id: c07a91517809
usage_count: 1
last_used: 2026-06-16
---
# Good: Encode output for HTML context
sub safe_html($user_input) {
    return encode_entities($user_input);
}