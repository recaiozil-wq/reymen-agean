---
skill_id: 2d12f44b4bfc
usage_count: 1
last_used: 2026-06-16
---
# Good: Using context managers
def process_file(path: str) -> str:
    with open(path, 'r') as f:
        return f.read()