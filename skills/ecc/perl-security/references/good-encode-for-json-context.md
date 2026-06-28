---
skill_id: 06ef95121947
usage_count: 1
last_used: 2026-06-16
---
# Good: Encode for JSON context
use JSON::MaybeXS qw(encode_json);
sub safe_json($data) {
    return encode_json($data);  # Handles escaping
}