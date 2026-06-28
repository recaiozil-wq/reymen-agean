---
skill_id: c7d9010ecae9
usage_count: 1
last_used: 2026-06-16
---
## Phase 4: Security Scanning

### Dependency Vulnerabilities (Maven)

```bash
mvn org.owasp:dependency-check-maven:check
```

Review `target/dependency-check-report.html` for CVEs.

### Quarkus Security Audit

```bash