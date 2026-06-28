---
skill_id: 3b995c527a42
usage_count: 1
last_used: 2026-06-16
---
## 11. Navigation and Routing

### General principles (apply to any routing solution):
- [ ] One routing approach used consistently — no mixing imperative `Navigator.push` with a declarative router
- [ ] Route arguments are typed — no `Map<String, dynamic>` or `Object?` casting
- [ ] Route paths defined as constants, enums, or generated — no magic strings scattered in code
- [ ] Auth guards/redirects centralized — not duplicated across individual screens
- [ ] Deep links configured for both Android and iOS
- [ ] Deep link URLs validated and sanitized before navigation
- [ ] Navigation state is testable — route changes can be verified in tests
- [ ] Back behavior is correct on all platforms

---