---
skill_id: 22e5b534fe25
usage_count: 1
last_used: 2026-06-16
---
# Good: EAFP style
def get_value(dictionary: dict, key: str, default_value: Any = None) -> Any:
    try:
        return dictionary[key]
    except KeyError:
        return default_value