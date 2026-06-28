---
skill_id: f96bc8600148
usage_count: 1
last_used: 2026-06-16
---
# Bad — YAGNI violation
class User:
    def __init__(self, name, email):
        self.name = name
        self.email = email
        self.preferences = {}  # Not needed yet!
        self.metadata = {}     # Not needed yet!