---
skill_id: f0319e214ea8
usage_count: 1
last_used: 2026-06-16
---
# 4. Commit
git add src/auth/login.py tests/test_login.py
git commit -m "fix: correct redirect URL after login

Preserves the ?next= parameter instead of always redirecting to /dashboard."