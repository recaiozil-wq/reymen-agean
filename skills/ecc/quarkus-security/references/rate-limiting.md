---
skill_id: b1e47b6225c7
usage_count: 1
last_used: 2026-06-16
---
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