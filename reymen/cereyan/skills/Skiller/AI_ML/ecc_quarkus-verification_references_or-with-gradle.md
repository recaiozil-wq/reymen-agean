---
name: ecc_quarkus-verification_references_or-with-gradle
description: Or with Gradle
title: "Ecc Quarkus Verification References Or With Gradle"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Or with Gradle |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Or with Gradle
./gradlew test jacocoTestReport jacocoTestCoverageVerification
```

### Test Categories

#### Unit Tests
Test service logic with mocked dependencies:

```java
@ExtendWith(MockitoExtension.class)
class UserServiceTest {
  @Mock UserRepository userRepository;
  @InjectMocks UserService userService;

  @Test
  void createUser_validInput_returnsUser() {
    var dto = new CreateUserDto("Alice", "alice@example.com");

    // Panache persist() is void — use doNothing + verify
    doNothing().when(userRepository).persist(any(User.class));

    User result = userService.create(dto);

    assertThat(result.name).isEqualTo("Alice");
    verify(userRepository).persist(any(User.class));
  }
}
```

#### Integration Tests
Test with real database (Testcontainers):

```java
@QuarkusTest
@QuarkusTestResource(PostgresTestResource.class)
class UserRepositoryIntegrationTest {

  @Inject
  UserRepository userRepository;

  @Test
  @Transactional
  void findByEmail_existingUser_returnsUser() {
    User user = new User();
    user.name = "Alice";
    user.email = "alice@example.com";
    userRepository.persist(user);

    Optional<User> found = userRepository.findByEmail("alice@example.com");

    assertThat(found).isPresent();
    assertThat(found.get().name).isEqualTo("Alice");
  }
}
```

#### API Tests
Test REST endpoints with REST Assured:

```java
@QuarkusTest
class UserResourceTest {

  @Test
  void createUser_validInput_returns201() {
    given()
        .contentType(ContentType.JSON)
        .body("""
            {"name": "Alice", "email": "alice@example.com"}
            """)
        .when().post("/api/users")
        .then()
        .statusCode(201)
        .body("name", equalTo("Alice"));
  }

  @Test
  void createUser_invalidEmail_returns400() {
    given()
        .contentType(ContentType.JSON)
        .body("""
            {"name": "Alice", "email": "invalid"}
            """)
        .when().post("/api/users")
        .then()
        .statusCode(400);
  }
}
```

### Coverage Report

Check `target/site/jacoco/index.html` for detailed coverage:
- Overall line coverage (target: 80%+)
- Branch coverage (target: 70%+)
- Identify uncovered critical paths
