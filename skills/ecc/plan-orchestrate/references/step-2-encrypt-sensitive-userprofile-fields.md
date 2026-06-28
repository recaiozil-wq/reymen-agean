---
skill_id: a052cd4a7bd2
usage_count: 1
last_used: 2026-06-16
---
## Step 2 — Encrypt sensitive UserProfile fields

**Intent**: Introduce an `EncryptedString` SQLAlchemy type and AES-GCM encrypt `birth_datetime` / `location` before persistence; load the key from an environment variable.
**Tags**: impl, security, db
**Chain rationale**: Security-sensitive write path, so `security-reviewer` closes the chain; `database-reviewer` validates the alembic migration; `python-reviewer` covers typing and PEP 8.

```bash
/everything-claude-code:orchestrate custom "everything-claude-code:tdd-guide,everything-claude-code:database-reviewer,everything-claude-code:python-reviewer,everything-claude-code:security-reviewer" "[Plan: docs/plan/example-feature.md#step-2] Implement EncryptedString SQLAlchemy type and migrate UserProfile.birth_datetime/location columns; key from ENV APP_DB_KEY; Acceptance: encrypt/decrypt roundtrip tests pass; alembic upgrade/downgrade clean on empty DB; no plaintext in DB after migrate; Out of scope: cross-tenant profile sharing logic"
```
````

### Example 2 — Legacy mode, same step

If `ECC_MODE=legacy` were detected, the same step would be emitted as a single uniform command (no plugin-prefixed forms anywhere in the output):

```bash
/orchestrate custom "tdd-guide,database-reviewer,python-reviewer,security-reviewer" "[Plan: docs/plan/example-feature.md#step-2] ..."
```

The two examples above illustrate **the two possible outputs** for two different environments. A single skill invocation produces only one of them, end to end.