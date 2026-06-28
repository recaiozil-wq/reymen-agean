---
skill_id: 864eb247f2af
usage_count: 1
last_used: 2026-06-16
---
## Verification Checklist

### Code Quality
- [ ] Build passes without warnings
- [ ] Static analysis clean (no high/medium issues)
- [ ] Code follows team conventions
- [ ] No commented-out code or TODOs in PR

### Testing
- [ ] All tests pass
- [ ] Code coverage ≥ 80%
- [ ] Integration tests with real database
- [ ] Security tests pass
- [ ] Performance within acceptable limits

### Security
- [ ] No dependency vulnerabilities
- [ ] Authentication/authorization tested
- [ ] Input validation complete
- [ ] Secrets not in source code
- [ ] Security headers configured

### Deployment
- [ ] Native compilation successful
- [ ] Container image builds
- [ ] Health checks respond correctly
- [ ] Configuration valid for target environment

### Native Image
- [ ] Native executable builds
- [ ] Native tests pass
- [ ] Startup time < 100ms
- [ ] Memory footprint acceptable