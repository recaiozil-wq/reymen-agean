---
skill_id: 824e437ab474
usage_count: 1
last_used: 2026-06-16
---
## Integration Tests with Real Database

```java
@QuarkusTest
@TestProfile(IntegrationTestProfile.class)
@DisplayName("Document Integration Tests")
class DocumentIntegrationTest {

  @Test
  @Transactional
  @DisplayName("Should create and retrieve document via API")
  void givenNewDocument_whenCreateAndRetrieve_thenSuccessful() {
    // ACT - Create via API
    Long id = given()
        .contentType(ContentType.JSON)
        .body("""
            {
              "referenceNumber": "INT-001",
              "description": "Integration test",
              "validUntil": "2030-01-01T00:00:00Z",
              "categories": ["test"]
            }
            """)
        .when().post("/api/documents")
        .then()
        .statusCode(201)
        .extract().path("id");

    // ASSERT - Retrieve via API
    given()
        .when().get("/api/documents/" + id)
        .then()
        .statusCode(200)
        .body("referenceNumber", equalTo("INT-001"));
  }
}
```