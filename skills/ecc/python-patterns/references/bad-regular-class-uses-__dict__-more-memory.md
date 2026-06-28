---
skill_id: 97e9596656b9
usage_count: 1
last_used: 2026-06-16
---
# Bad: Regular class uses __dict__ (more memory)
class Point:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y