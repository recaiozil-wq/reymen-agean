---
skill_id: 535654523e7f
usage_count: 1
last_used: 2026-06-16
---
# Coverage with race detection
go test -race -coverprofile=coverage.out ./...
```

### Coverage Targets

| Code Type | Target |
|-----------|--------|
| Critical business logic | 100% |
| Public APIs | 90%+ |
| General code | 80%+ |
| Generated code | Exclude |

### Excluding Generated Code from Coverage

```go
//go:generate mockgen -source=interface.go -destination=mock_interface.go

// In coverage profile, exclude with build tags:
// go test -cover -tags=!generate ./...
```