---
skill_id: a61003103aa9
usage_count: 1
last_used: 2026-06-16
---
# Windows: start build/reports/kover/html/index.html
```

#### Coverage Targets

| Code Type | Target |
|-----------|--------|
| Critical business logic | 100% |
| Public APIs | 90%+ |
| General code | 80%+ |
| Generated / config code | Exclude |

### Ktor testApplication Testing

```kotlin
class ApiRoutesTest : FunSpec({
    test("GET /users returns list") {
        testApplication {
            application {
                configureRouting()
                configureSerialization()
            }

            val response = client.get("/users")

            response.status shouldBe HttpStatusCode.OK
            val users = response.body<List<UserResponse>>()
            users.shouldNotBeEmpty()
        }
    }

    test("POST /users creates user") {
        testApplication {
            application {
                configureRouting()
                configureSerialization()
            }

            val response = client.post("/users") {
                contentType(ContentType.Application.Json)
                setBody(CreateUserRequest("Alice", "alice@example.com"))
            }

            response.status shouldBe HttpStatusCode.Created
        }
    }
})
```

### Testing Commands

```bash