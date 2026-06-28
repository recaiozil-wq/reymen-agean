---
skill_id: b06ea556dda3
usage_count: 1
last_used: 2026-06-16
---
## Immutability

```java
// PASS: Favor records and final fields
public record MarketDto(Long id, String name, MarketStatus status) {}

public class Market {
  private final Long id;
  private final String name;
  // getters only, no setters
}

// PASS: [QUARKUS] Panache active-record entities use public fields (Quarkus convention)
@Entity
public class Market extends PanacheEntity {
  public String name;
  public MarketStatus status;
  // Panache generates accessors at build time; public fields are idiomatic here
}

// PASS: [QUARKUS] Panache MongoDB entities
@MongoEntity(collection = "markets")
public class Market extends PanacheMongoEntity {
  public String name;
  public MarketStatus status;
}
```