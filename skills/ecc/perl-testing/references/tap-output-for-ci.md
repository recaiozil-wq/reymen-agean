---
skill_id: 7dce323859c7
usage_count: 1
last_used: 2026-06-16
---
# TAP output for CI
prove -l --formatter TAP::Formatter::JUnit t/ > results.xml
```

### .proverc Configuration

```text
-l
--color
--timer
-r
-j4
--state=save
```