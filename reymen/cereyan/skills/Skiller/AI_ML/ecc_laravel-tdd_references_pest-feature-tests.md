---
name: ecc_laravel-tdd_references_pest-feature-tests
description: Pest Feature Tests
title: "Ecc Laravel Tdd References Pest Feature Tests"
version: 1.0.0
---

| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** |  |
| **Nerede** | `AI_ML/ecc_laravel-tdd_references_pest-feature-tests.md` |
| **Ne Zaman** |  |
| **Neden** |  |
| **Nasıl** |  |

## Pest Feature Tests

```php
<?php

use App\Models\Product;
use App\Models\User;

uses(\Illuminate\Foundation\Testing\RefreshDatabase::class);

beforeEach(function () {
    $this->user = User::factory()->create();
    $this->actingAs($this->user);
});

it('lists products', function () {
    Product::factory()->count(3)->create(['user_id' => $this->user->id]);

    $this->get(route('products.index'))
        ->assertOk()
        ->assertViewHas('products');
});

it('creates a product with valid data', function () {
    $this->post(route('products.store'), [
        'name' => 'Test Product', 'price' => 1999,
    ])->assertRedirect();

    $this->assertDatabaseHas('products', ['name' => 'Test Product']);
});

it('fails validation without required fields', function () {
    $this->post(route('products.store'), [])
        ->assertSessionHasErrors(['name', 'price']);
});

it('authorizes updates', function () {
    $other = User::factory()->create();
    $product = Product::factory()->create(['user_id' => $other->id]);

    $this->put(route('products.update', $product), ['name' => 'Hacked'])
        ->assertForbidden();
});
```
