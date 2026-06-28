---
skill_id: 1e180c256e95
usage_count: 1
last_used: 2026-06-16
---
## Output Encoding

Always encode output for its context: `HTML::Entities::encode_entities()` for HTML, `URI::Escape::uri_escape_utf8()` for URLs, `JSON::MaybeXS::encode_json()` for JSON.