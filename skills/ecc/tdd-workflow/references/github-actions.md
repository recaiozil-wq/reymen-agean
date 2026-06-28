---
skill_id: aceff8d94cb8
usage_count: 1
last_used: 2026-06-16
---
# GitHub Actions
- name: Run Tests
  run: npm test -- --coverage
- name: Upload Coverage
  uses: codecov/codecov-action@v3
```