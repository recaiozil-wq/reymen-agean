---
skill_id: 6534b33e7a07
usage_count: 1
last_used: 2026-06-16
---
## 15. Static Analysis

### Configuration:
- [ ] `analysis_options.yaml` present with strict settings enabled
- [ ] Strict analyzer settings: `strict-casts: true`, `strict-inference: true`, `strict-raw-types: true`
- [ ] A comprehensive lint rule set is included (very_good_analysis, flutter_lints, or custom strict rules)
- [ ] All sub-packages in monorepos inherit or share the root analysis options

### Enforcement:
- [ ] No unresolved analyzer warnings in committed code
- [ ] Lint suppressions (`// ignore:`) are justified with comments explaining why
- [ ] `flutter analyze` runs in CI and failures block merges

### Key rules to verify regardless of lint package:
- [ ] `prefer_const_constructors` — performance in widget trees
- [ ] `avoid_print` — use proper logging
- [ ] `unawaited_futures` — prevent fire-and-forget async bugs
- [ ] `prefer_final_locals` — immutability at variable level
- [ ] `always_declare_return_types` — explicit contracts
- [ ] `avoid_catches_without_on_clauses` — specific error handling
- [ ] `always_use_package_imports` — consistent import style

---