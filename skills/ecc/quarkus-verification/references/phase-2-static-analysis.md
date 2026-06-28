---
skill_id: 82dce141f1fe
usage_count: 1
last_used: 2026-06-16
---
## Phase 2: Static Analysis

### Checkstyle, PMD, SpotBugs (Maven)

```bash
mvn checkstyle:check pmd:check spotbugs:check
```

### SonarQube (if configured)

```bash
mvn sonar:sonar \
  -Dsonar.projectKey=my-quarkus-project \
  -Dsonar.host.url=http://localhost:9000 \
  -Dsonar.login=${SONAR_TOKEN}
```

### Common Issues to Address

- Unused imports or variables
- Complex methods (high cyclomatic complexity)
- Potential null pointer dereferences
- Security issues flagged by SpotBugs