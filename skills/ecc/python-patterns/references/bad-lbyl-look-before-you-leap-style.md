---
skill_id: 43ac95b03243
usage_count: 1
last_used: 2026-06-16
---
# Bad: LBYL (Look Before You Leap) style
def get_value(dictionary: dict, key: str, default_value: Any = None) -> Any:
    if key in dictionary:
        return dictionary[key]
    else:
        return default_value
```