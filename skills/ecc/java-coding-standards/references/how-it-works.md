---
skill_id: 4f9625493343
usage_count: 1
last_used: 2026-06-16
---
## How It Works

### Framework Detection

Before applying standards, determine the framework from the build file:

- Build file contains `quarkus` → apply **[QUARKUS]** conventions
- Build file contains `spring-boot` → apply **[SPRING]** conventions
- Neither detected → apply shared conventions only