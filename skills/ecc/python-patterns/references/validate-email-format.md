---
skill_id: ac14c1254377
usage_count: 1
last_used: 2026-06-16
---
# Validate email format
        if "@" not in self.email:
            raise ValueError(f"Invalid email: {self.email}")