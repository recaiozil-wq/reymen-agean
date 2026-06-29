---
name: ecc_quarkus-security_references_rate-limiting
description: Rate Limiting
title: "Ecc Quarkus Security References Rate Limiting"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Rate Limiting |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

## Rate Limiting

**Security Note**: Never use `X-Forwarded-For` directly — clients can spoof it.
Use the actual remote address from the servlet request, or an authenticated
identity (API key, JWT subject) when available.

```java
@ApplicationScoped
public class RateLimitFilter implements ContainerRequestFilter {
  private final Map<String, RateLimiter> limiters = new ConcurrentHashMap<>();

  @Inject
  HttpServletRequest servletRequest;

  @Override
  public void filter(ContainerRequestContext requestContext) {
    String clientId = getClientIdentifier();
    RateLimiter limiter = limiters.computeIfAbsent(clientId,
        k -> RateLimiter.create(100.0)); // 100 requests per second

    if (!limiter.tryAcquire()) {
      requestContext.abortWith(
          Response.status(429)
              .entity(Map.of("error", "Too many requests"))
              .build()
      );
    }
  }

  private String getClientIdentifier() {
    // Use the container-provided remote address (not X-Forwarded-For).
    // If behind a trusted proxy, configure quarkus.http.proxy.proxy-address-forwarding=true
    // so getRemoteAddr() returns the real client IP.
    return servletRequest.getRemoteAddr();
  }
}
```
