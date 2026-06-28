---
skill_id: 5c25c49c36a2
usage_count: 1
last_used: 2026-06-16
---
## JSON API Testing

```php
namespace Tests\Feature\Http\Controllers\Api;

use App\Models\Product;
use App\Models\User;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Tests\TestCase;

class ProductApiTest extends TestCase
{
    use RefreshDatabase;

    public function test_unauthenticated_requests_are_rejected(): void
    {
        $this->getJson('/api/products')->assertUnauthorized();
    }

    public function test_it_lists_paginated_products(): void
    {
        $user = User::factory()->create();
        Product::factory()->count(5)->create(['user_id' => $user->id]);

        $response = $this->actingAs($user)->getJson('/api/products');

        $response->assertOk();
        $response->assertJsonCount(5, 'data');
        $response->assertJsonStructure([
            'data' => [['id', 'name', 'price']],
            'meta' => ['current_page', 'last_page', 'total'],
        ]);
    }

    public function test_it_creates_a_product(): void
    {
        $user = User::factory()->create();

        $response = $this->actingAs($user)->postJson('/api/products', [
            'name' => 'API Product',
            'price' => 4999,
        ]);

        $response->assertCreated();
        $response->assertJsonPath('data.name', 'API Product');
    }

    public function test_users_cannot_delete_others_products(): void
    {
        $owner = User::factory()->create();
        $attacker = User::factory()->create();
        $product = Product::factory()->create(['user_id' => $owner->id]);

        $this->actingAs($attacker)
            ->deleteJson("/api/products/{$product->id}")
            ->assertForbidden();
    }
}
```