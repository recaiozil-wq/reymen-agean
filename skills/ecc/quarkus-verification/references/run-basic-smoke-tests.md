---
skill_id: 5ffcb5d3afc2
usage_count: 1
last_used: 2026-06-16
---
# Run basic smoke tests
curl http://localhost:8080/q/health/live
curl http://localhost:8080/q/health/ready
```

### Native Image Troubleshooting

Common issues:
- **Reflection**: Add reflection config for dynamic classes
- **Resources**: Include resources with `quarkus.native.resources.includes`
- **JNI**: Register JNI classes if using native libraries

Example reflection config:
```java
@RegisterForReflection(targets = {MyDynamicClass.class})
public class ReflectionConfiguration {}
```