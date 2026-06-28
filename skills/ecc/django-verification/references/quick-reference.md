---
skill_id: c0065bf89a81
usage_count: 1
last_used: 2026-06-16
---
## Quick Reference

| Check | Command |
|-------|---------|
| Environment | `python --version` |
| Type checking | `mypy .` |
| Linting | `ruff check .` |
| Formatting | `black . --check` |
| Migrations | `python manage.py makemigrations --check` |
| Tests | `pytest --cov=apps` |
| Security | `pip-audit && bandit -r .` |
| Django check | `python manage.py check --deploy` |
| Collectstatic | `python manage.py collectstatic --noinput` |
| Diff stats | `git diff --stat` |

Remember: Automated verification catches common issues but doesn't replace manual code review and testing in staging environment.