---
name: ecc_quarkus-security_references_oidc
description: OIDC
title: "Ecc Quarkus Security References Oidc"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | OIDC |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# OIDC
quarkus.oidc.auth-server-url=https://auth.example.com/realms/myrealm
quarkus.oidc.client-id=backend-service
quarkus.oidc.credentials.secret=${OIDC_SECRET}
```

### Custom Authentication Filter

```java
@Provider
@Priority(Priorities.AUTHENTICATION)
public class CustomAuthFilter implements ContainerRequestFilter {

  @Inject
  SecurityIdentity identity;

  @Override
  public void filter(ContainerRequestContext requestContext) {
    String authHeader = requestContext.getHeaderString(HttpHeaders.AUTHORIZATION);

    // Reject immediately if header is absent or malformed
    if (authHeader == null || !authHeader.startsWith("Bearer ")) {
      requestContext.abortWith(Response.status(Response.Status.UNAUTHORIZED).build());
      return;
    }

    String token = authHeader.substring(7);
    if (!validateToken(token)) {
      requestContext.abortWith(Response.status(Response.Status.UNAUTHORIZED).build());
    }
  }

  private boolean validateToken(String token) {
    // Token validation logic
    return true;
  }
}
```
