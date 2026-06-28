---
name: ecc_quarkus-tdd_references_integration-tests-with-real-database
description: Integration Tests with Real Database
title: "Ecc Quarkus Tdd References Integration Tests With Real Database"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Integration Tests with Real Database |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

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
