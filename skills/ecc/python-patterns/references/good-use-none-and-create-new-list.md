---
skill_id: 04f2b88ce8ef
usage_count: 1
last_used: 2026-06-16
---
# Good: Use None and create new list
def append_to(item, items=None):
    if items is None:
        items = []
    items.append(item)
    return items