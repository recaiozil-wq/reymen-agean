---
skill_id: f108f5435d7c
usage_count: 1
last_used: 2026-06-16
---
## Model Factories

```php
// database/factories/UserFactory.php
class UserFactory extends Factory
{
    protected static ?string $password = null;

    public function definition(): array
    {
        return [
            'name' => fake()->name(),
            'email' => fake()->unique()->safeEmail(),
            'email_verified_at' => now(),
            'password' => static::$password ??= Hash::make('password'),
            'remember_token' => Str::random(10),
            'role' => 'user',
        ];
    }

    public function admin(): static
    {
        return $this->state(fn (array $attributes) => ['role' => 'admin']);
    }

    public function unverified(): static
    {
        return $this->state(fn (array $attributes) => ['email_verified_at' => null]);
    }
}

// database/factories/ProductFactory.php
class ProductFactory extends Factory
{
    public function definition(): array
    {
        return [
            'name' => fake()->unique()->words(3, true),
            'slug' => fn (array $attrs) => Str::slug($attrs['name']),
            'description' => fake()->paragraph(),
            'price' => fake()->numberBetween(100, 100000),
            'stock' => fake()->numberBetween(0, 100),
            'is_active' => true,
            'user_id' => UserFactory::new(),
        ];
    }

    public function outOfStock(): static
    {
        return $this->state(fn (array $attributes) => ['stock' => 0]);
    }
}
```

### Using Factories

```php
$user = User::factory()->create();
$admin = User::factory()->admin()->create();
$product = Product::factory()->create(['user_id' => $user->id]);
$products = Product::factory()->count(10)->create();
$draft = Product::factory()->make(); // Not persisted

// With relationships
$user = User::factory()->has(Product::factory()->count(3))->create();

// Sequences
User::factory()->count(3)->sequence(
    ['role' => 'admin'], ['role' => 'editor'], ['role' => 'user'],
)->create();
```