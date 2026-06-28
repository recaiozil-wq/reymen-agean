---
skill_id: 6a6ec4377afc
usage_count: 1
last_used: 2026-06-16
---
## Security Headers

```java
@Provider
public class SecurityHeadersFilter implements ContainerResponseFilter {

  @Override
  public void filter(ContainerRequestContext request, ContainerResponseContext response) {
    MultivaluedMap<String, Object> headers = response.getHeaders();

    // Prevent clickjacking
    headers.putSingle("X-Frame-Options", "DENY");

    // XSS protection
    headers.putSingle("X-Content-Type-Options", "nosniff");
    headers.putSingle("X-XSS-Protection", "1; mode=block");

    // HSTS
    headers.putSingle("Strict-Transport-Security", "max-age=31536000; includeSubDomains");

    // CSP — avoid 'unsafe-inline' for script-src as it negates XSS protection;
    // use nonces or hashes instead. 'unsafe-inline' for style-src is acceptable
    // when CSS frameworks require it, but prefer nonces where possible.
    headers.putSingle("Content-Security-Policy",
        "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'");
  }
}
```