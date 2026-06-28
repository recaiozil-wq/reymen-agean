---
skill_id: 8d413bea2271
usage_count: 1
last_used: 2026-06-16
---
## Repository Pattern (Panache Repository)

```java
@ApplicationScoped
public class DocumentRepository implements PanacheRepository<Document> {

  public List<Document> findByStatus(DocumentStatus status, int page, int size) {
    return find("status = ?1 order by createdAt desc", status)
        .page(page, size)
        .list();
  }

  public Optional<Document> findByReferenceNumber(String referenceNumber) {
    return find("referenceNumber", referenceNumber).firstResultOptional();
  }

  public long countByStatusAndDate(DocumentStatus status, LocalDate date) {
    return count("status = ?1 and createdAt >= ?2", status, date.atStartOfDay());
  }
}
```