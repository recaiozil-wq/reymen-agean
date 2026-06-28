---
skill_id: c0065bf89a81
usage_count: 1
last_used: 2026-06-16
---
## Quick Reference

| AI Regression Pattern | Test Strategy | Priority |
|---|---|---|
| Sandbox/production mismatch | Assert same response shape in sandbox mode |  High |
| SELECT clause omission | Assert all required fields in response |  High |
| Error state leakage | Assert state cleanup on error |  Medium |
| Missing rollback | Assert state restored on API failure |  Medium |
| Type cast masking null | Assert field is not undefined |  Medium |