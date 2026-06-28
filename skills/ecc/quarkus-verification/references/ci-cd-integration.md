---
skill_id: 1c2d2cd0f489
usage_count: 1
last_used: 2026-06-16
---
## CI/CD Integration

### GitHub Actions Example

```yaml
name: Verification

on: [push, pull_request]

jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up JDK 21
        uses: actions/setup-java@v3
        with:
          java-version: '21'
          distribution: 'temurin'

      - name: Cache Maven packages
        uses: actions/cache@v3
        with:
          path: ~/.m2
          key: ${{ runner.os }}-m2-${{ hashFiles('**/pom.xml') }}

      - name: Build
        run: mvn clean verify -DskipTests

      - name: Test with Coverage
        run: mvn test jacoco:report jacoco:check

      - name: Security Scan
        run: mvn org.owasp:dependency-check-maven:check

      - name: Upload Coverage
        uses: codecov/codecov-action@v3
        with:
          files: target/site/jacoco/jacoco.xml
```