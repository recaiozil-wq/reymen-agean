---
skill_id: 5bb5ab164c4e
usage_count: 1
last_used: 2026-06-16
---
# Pattern matching
like($error, qr/not found/i, 'error mentions not found');
unlike($output, qr/password/, 'output hides password');