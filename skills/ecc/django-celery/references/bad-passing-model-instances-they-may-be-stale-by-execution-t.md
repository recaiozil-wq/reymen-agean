---
skill_id: 6e1edbaeaea7
usage_count: 1
last_used: 2026-06-16
---
# BAD: Passing model instances — they may be stale by execution time
send_welcome_email.delay(user)        # Never pass ORM objects
send_welcome_email.delay(user.pk)     # Always pass PKs