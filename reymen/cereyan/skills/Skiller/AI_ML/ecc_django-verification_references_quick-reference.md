
> **Kategori:** AI_ML

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Tüm ajanlar |
| **Ne?** | Ecc_Django Verification_References_Quick Reference |
| **Nerede?** | AI_ML/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

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