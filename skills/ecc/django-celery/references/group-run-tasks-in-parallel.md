---
skill_id: 015450937c19
usage_count: 1
last_used: 2026-06-16
---
# Group: run tasks in parallel
parallel = group(
    send_welcome_email.s(user_id)
    for user_id in new_user_ids
)
parallel.delay()