---
skill_id: b01e72df1fdb
usage_count: 1
last_used: 2026-06-16
---
## Pagination and Sorting

```java
PageRequest page = PageRequest.of(pageNumber, pageSize, Sort.by("createdAt").descending());
Page<Market> results = marketService.list(page);
```