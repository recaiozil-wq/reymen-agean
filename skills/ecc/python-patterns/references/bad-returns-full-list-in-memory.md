---
skill_id: 036f4c0beab8
usage_count: 1
last_used: 2026-06-16
---
# Bad: Returns full list in memory
def read_lines(path: str) -> list[str]:
    with open(path) as f:
        return [line.strip() for line in f]