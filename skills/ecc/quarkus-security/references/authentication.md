---
skill_id: 6fa691d2c07b
usage_count: 1
last_used: 2026-06-16
---
## Authentication

### JWT Authentication

```java
// Resource protected with JWT
@Path("/api/protected")
@Authenticated
public class ProtectedResource {

  @Inject
  JsonWebToken jwt;

  @Inject
  SecurityIdentity securityIdentity;

  @GET
  public Response getData() {
    String username = jwt.getName();
    Set<String> roles = jwt.getGroups();
    return Response.ok(Map.of(
        "username", username,
        "roles", roles,
        "principal", securityIdentity.getPrincipal().getName()
    )).build();
  }
}
```

Configuration (application.properties):
```properties
mp.jwt.verify.publickey.location=publicKey.pem
mp.jwt.verify.issuer=https://auth.example.com