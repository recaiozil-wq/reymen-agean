---
skill_id: 3d56a64feb18
usage_count: 1
last_used: 2026-06-16
---
# GOOD: Escape first, then mark safe
def render_good(user_input):
    return mark_safe(escape(user_input))