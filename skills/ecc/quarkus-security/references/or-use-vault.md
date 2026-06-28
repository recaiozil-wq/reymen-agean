---
skill_id: 90fe5f20de47
usage_count: 1
last_used: 2026-06-16
---
# Or use Vault
quarkus.vault.url=https://vault.example.com
quarkus.vault.authentication.kubernetes.role=my-role
```

### HashiCorp Vault Integration

```java
@ApplicationScoped
public class SecretService {

  @ConfigProperty(name = "api-key")
  String apiKey; // Fetched from Vault

  public String getSecret(String key) {
    return ConfigProvider.getConfig().getValue(key, String.class);
  }
}
```