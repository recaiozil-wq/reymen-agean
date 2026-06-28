---
skill_id: c22968930a25
usage_count: 1
last_used: 2026-06-16
---
# Schedule in the future
send_reminder.apply_async(args=[user.pk], countdown=3600)  # 1 hour from now
send_reminder.apply_async(args=[user.pk], eta=timezone.now() + timedelta(days=1))