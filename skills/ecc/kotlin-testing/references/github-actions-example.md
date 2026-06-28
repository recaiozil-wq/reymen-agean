---
skill_id: 98c75cc72ab5
usage_count: 1
last_used: 2026-06-16
---
# GitHub Actions example
test:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-java@v4
      with:
        distribution: 'temurin'
        java-version: '21'

    - name: Run tests with coverage
      run: ./gradlew test koverXmlReport

    - name: Verify coverage
      run: ./gradlew koverVerify

    - name: Upload coverage
      uses: codecov/codecov-action@v5
      with:
        files: build/reports/kover/report.xml
        token: ${{ secrets.CODECOV_TOKEN }}
```

**Remember**: Tests are documentation. They show how your Kotlin code is meant to be used. Use Kotest's expressive matchers to make tests readable and MockK for clean mocking of dependencies.