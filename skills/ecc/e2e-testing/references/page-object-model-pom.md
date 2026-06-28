---
skill_id: 6ed9d4f2b598
usage_count: 1
last_used: 2026-06-16
---
## Page Object Model (POM)

```typescript
import { Page, Locator } from '@playwright/test'

export class ItemsPage {
  readonly page: Page
  readonly searchInput: Locator
  readonly itemCards: Locator
  readonly createButton: Locator

  constructor(page: Page) {
    this.page = page
    this.searchInput = page.locator('[data-testid="search-input"]')
    this.itemCards = page.locator('[data-testid="item-card"]')
    this.createButton = page.locator('[data-testid="create-btn"]')
  }

  async goto() {
    await this.page.goto('/items')
    await this.page.waitForLoadState('networkidle')
  }

  async search(query: string) {
    await this.searchInput.fill(query)
    await this.page.waitForResponse(resp => resp.url().includes('/api/search'))
    await this.page.waitForLoadState('networkidle')
  }

  async getItemCount() {
    return await this.itemCards.count()
  }
}
```