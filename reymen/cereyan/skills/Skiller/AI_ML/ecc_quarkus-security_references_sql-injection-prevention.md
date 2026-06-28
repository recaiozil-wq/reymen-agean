---
name: ecc_quarkus-security_references_sql-injection-prevention
description: SQL Injection Prevention
title: "Ecc Quarkus Security References Sql Injection Prevention"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | SQL Injection Prevention |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

## SQL Injection Prevention

### Panache Active Record (Safe by Default)

```java
// GOOD: Parameterized queries with Panache
List<User> users = User.list("email = ?1 and active = ?2", email, true);

Optional<User> user = User.find("username", username).firstResultOptional();

// GOOD: Named parameters
List<User> users = User.list("email = :email and age > :minAge",
    Parameters.with("email", email).and("minAge", 18));
```

### Native Queries (Use Parameters)

```java
// BAD: String concatenation
@Query(value = "SELECT * FROM users WHERE name = '" + name + "'", nativeQuery = true)

// GOOD: Parameterized native query
@Entity
public class User extends PanacheEntity {
  public static List<User> findByEmailNative(String email) {
    return getEntityManager()
        .createNativeQuery("SELECT * FROM users WHERE email = :email", User.class)
        .setParameter("email", email)
        .getResultList();
  }
}
```
