---
skill_id: f7d930d9ad28
usage_count: 1
last_used: 2026-06-16
---
## Financial / Critical Flow Testing

```typescript
test('trade execution', async ({ page }) => {
  // Skip on production — real money
  test.skip(process.env.NODE_ENV === 'production', 'Skip on production')

  await page.goto('/markets/test-market')
  await page.locator('[data-testid="position-yes"]').click()
  await page.locator('[data-testid="trade-amount"]').fill('1.0')

  // Verify preview
  const preview = page.locator('[data-testid="trade-preview"]')
  await expect(preview).toContainText('1.0')

  // Confirm and wait for blockchain
  await page.locator('[data-testid="confirm-trade"]').click()
  await page.waitForResponse(
    resp => resp.url().includes('/api/trade') && resp.status() === 200,
    { timeout: 30000 }
  )

  await expect(page.locator('[data-testid="trade-success"]')).toBeVisible()
})
```