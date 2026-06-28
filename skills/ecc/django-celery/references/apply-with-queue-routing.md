---
skill_id: 263987ee5dac
usage_count: 1
last_used: 2026-06-16
---
# Apply with queue routing
sync_contact_to_crm.apply_async(args=[contact.pk], queue='high_priority')