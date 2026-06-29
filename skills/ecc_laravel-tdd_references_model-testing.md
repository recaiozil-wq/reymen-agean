---
name: ecc_laravel-tdd_references_model-testing
description: Model Testing
title: "Ecc Laravel Tdd References Model Testing"
version: 1.0.0
---

| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** |  |
| **Nerede** | `AI_ML/ecc_laravel-tdd_references_model-testing.md` |
| **Ne Zaman** |  |
| **Neden** |  |
| **Nasıl** |  |

## Model Testing

```php
namespace Tests\Unit\Models;

use App\Models\User;
use App\Models\Product;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Tests\TestCase;

class UserTest extends TestCase
{
    use RefreshDatabase;

    public function test_it_hides_sensitive_attributes(): void
    {
        $user = User::factory()->create();
        $this->assertArrayNotHasKey('password', $user->toArray());
    }

    public function test_admin_scope_returns_only_admins(): void
    {
        User::factory()->admin()->create();
        User::factory()->count(3)->create();

        $this->assertCount(1, User::admin()->get());
    }
}

class ProductTest extends TestCase
{
    use RefreshDatabase;

    public function test_active_scope_filters_correctly(): void
    {
        Product::factory()->count(3)->create(['is_active' => true]);
        Product::factory()->count(2)->create(['is_active' => false]);

        $this->assertCount(3, Product::active()->get());
    }

    public function test_it_belongs_to_a_user(): void
    {
        $user = User::factory()->create();
        $product = Product::factory()->create(['user_id' => $user->id]);

        $this->assertTrue($product->user->is($user));
    }
}
```
