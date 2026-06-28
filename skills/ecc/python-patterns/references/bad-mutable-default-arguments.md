---
skill_id: a0773227b847
usage_count: 1
last_used: 2026-06-16
---
# Bad: Mutable default arguments
def append_to(item, items=[]):
    items.append(item)
    return items