---
skill_id: 364dd4a6f0cd
usage_count: 1
last_used: 2026-06-16
---
# BAD: Never mark user input as safe without escaping
def render_bad(user_input):
    return mark_safe(user_input)  # VULNERABLE!