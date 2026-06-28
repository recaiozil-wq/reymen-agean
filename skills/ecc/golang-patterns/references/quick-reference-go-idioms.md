---
skill_id: 80a33b74d66f
usage_count: 1
last_used: 2026-06-16
---
## Quick Reference: Go Idioms

| Idiom | Description |
|-------|-------------|
| Accept interfaces, return structs | Functions accept interface params, return concrete types |
| Errors are values | Treat errors as first-class values, not exceptions |
| Don't communicate by sharing memory | Use channels for coordination between goroutines |
| Make the zero value useful | Types should work without explicit initialization |
| A little copying is better than a little dependency | Avoid unnecessary external dependencies |
| Clear is better than clever | Prioritize readability over cleverness |
| gofmt is no one's favorite but everyone's friend | Always format with gofmt/goimports |
| Return early | Handle errors first, keep happy path unindented |