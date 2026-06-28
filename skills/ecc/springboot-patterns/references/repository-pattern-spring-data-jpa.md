---
skill_id: 34bcd8c982a4
usage_count: 1
last_used: 2026-06-16
---
## Repository Pattern (Spring Data JPA)

```java
public interface MarketRepository extends JpaRepository<MarketEntity, Long> {
  @Query("select m from MarketEntity m where m.status = :status order by m.volume desc")
  List<MarketEntity> findActive(@Param("status") MarketStatus status, Pageable pageable);
}
```