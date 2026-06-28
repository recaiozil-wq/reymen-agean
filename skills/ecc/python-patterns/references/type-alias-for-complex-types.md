---
skill_id: 4cf78f795902
usage_count: 1
last_used: 2026-06-16
---
# Type alias for complex types
JSON = Union[dict[str, Any], list[Any], str, int, float, bool, None]

def parse_json(data: str) -> JSON:
    return json.loads(data)