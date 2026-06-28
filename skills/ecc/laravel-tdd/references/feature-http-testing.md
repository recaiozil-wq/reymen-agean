---
skill_id: e3fc46915e77
usage_count: 1
last_used: 2026-06-16
---
## Feature / HTTP Testing

```php
namespace Tests\Feature\Http\Controllers;

use App\Models\Product;
use App\Models\User;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Tests\TestCase;

class ProductControllerTest extends TestCase
{
    use RefreshDatabase;

    public function test_guests_are_redirected_to_login(): void
    {
        $this->get(route('products.create'))->assertRedirect(route('login'));
    }

    public function test_it_stores_a_new_product(): void
    {
        $user = User::factory()->create();
        $this->actingAs($user);

        $response = $this->post(route('products.store'), [
            'name' => 'New Product',
            'description' => 'Description',
            'price' => 2999,
            'stock' => 10,
        ]);

        $response->assertRedirect(route('products.index'));
        $this->assertDatabaseHas('products', [
            'name' => 'New Product',
            'user_id' => $user->id,
        ]);
    }

    public function test_it_validates_required_fields(): void
    {
        $this->actingAs(User::factory()->create());
        $this->post(route('products.store'), [])
            ->assertSessionHasErrors(['name', 'price']);
    }

    public function test_users_cannot_modify_others_products(): void
    {
        $owner = User::factory()->create();
        $attacker = User::factory()->create();
        $product = Product::factory()->create(['user_id' => $owner->id]);

        $this->actingAs($attacker)
            ->delete(route('products.destroy', $product))
            ->assertForbidden();
    }
}
```