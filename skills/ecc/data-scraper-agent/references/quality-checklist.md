---
skill_id: cfc594595bd4
usage_count: 1
last_used: 2026-06-16
---
## Quality Checklist

Before marking the agent complete:

- [ ] `config.yaml` controls all user-facing settings — no hardcoded values
- [ ] `profile/context.md` holds user-specific context for AI matching
- [ ] Deduplication by URL before every storage push
- [ ] Gemini client has model fallback chain (4 models)
- [ ] Batch size ≤ 5 items per API call
- [ ] `maxOutputTokens` ≥ 2048
- [ ] `.env` is in `.gitignore`
- [ ] `.env.example` provided for onboarding
- [ ] `setup.py` creates DB schema on first run
- [ ] `enrich_existing.py` backfills AI scores on old rows
- [ ] GitHub Actions workflow commits `feedback.json` after each run
- [ ] README covers: setup in < 5 minutes, required secrets, customisation

---