---
name: ecc_laravel-tdd_references_tdd-workflow-for-laravel
description: TDD Workflow for Laravel
title: "Ecc Laravel Tdd References Tdd Workflow For Laravel"
version: 1.0.0
---

| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** |  |
| **Nerede** | `AI_ML/ecc_laravel-tdd_references_tdd-workflow-for-laravel.md` |
| **Ne Zaman** |  |
| **Neden** |  |
| **Nasıl** |  |

## TDD Workflow for Laravel

### Red-Green-Refactor Cycle

```php
// Step 1: RED — Write a failing test
public function test_a_product_can_be_created(): void
{
    $product = Product::factory()->create(['name' => 'Test Product']);
    $this->assertDatabaseHas('products', ['name' => 'Test Product']);
}

// Step 2: GREEN — Write the migration, model, and factory
// Step 3: REFACTOR — Improve while keeping tests green
```
