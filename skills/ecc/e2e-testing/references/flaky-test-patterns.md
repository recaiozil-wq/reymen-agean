---
skill_id: 1a1ac0a78e56
usage_count: 1
last_used: 2026-06-16
---
## Flaky Test Patterns

### Quarantine

```typescript
test('flaky: complex search', async ({ page }) => {
  test.fixme(true, 'Flaky - Issue #123')
  // test code...
})

test('conditional skip', async ({ page }) => {
  test.skip(process.env.CI, 'Flaky in CI - Issue #123')
  // test code...
})
```

### Identify Flakiness

```bash
npx playwright test tests/search.spec.ts --repeat-each=10
npx playwright test tests/search.spec.ts --retries=3
```

### Common Causes & Fixes

**Race conditions:**
```typescript
// Bad: assumes element is ready
await page.click('[data-testid="button"]')

// Good: auto-wait locator
await page.locator('[data-testid="button"]').click()
```

**Network timing:**
```typescript
// Bad: arbitrary timeout
await page.waitForTimeout(5000)

// Good: wait for specific condition
await page.waitForResponse(resp => resp.url().includes('/api/data'))
```

**Animation timing:**
```typescript
// Bad: click during animation
await page.click('[data-testid="menu-item"]')

// Good: wait for stability
await page.locator('[data-testid="menu-item"]').waitFor({ state: 'visible' })
await page.waitForLoadState('networkidle')
await page.locator('[data-testid="menu-item"]').click()
```