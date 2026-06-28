---
skill_id: 2e17840ededd
usage_count: 1
last_used: 2026-06-16
---
## Streams Best Practices

```java
// PASS: Use streams for transformations, keep pipelines short
List<String> names = markets.stream()
    .map(Market::name)
    .filter(Objects::nonNull)
    .toList();

// FAIL: Avoid complex nested streams; prefer loops for clarity
```