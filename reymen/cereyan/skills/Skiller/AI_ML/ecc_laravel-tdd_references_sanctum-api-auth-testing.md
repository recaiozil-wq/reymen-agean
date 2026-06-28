---
name: ecc_laravel-tdd_references_sanctum-api-auth-testing
description: Sanctum API Auth Testing
title: "Ecc Laravel Tdd References Sanctum Api Auth Testing"
version: 1.0.0
---

| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** |  |
| **Nerede** | `AI_ML/ecc_laravel-tdd_references_sanctum-api-auth-testing.md` |
| **Ne Zaman** |  |
| **Neden** |  |
| **Nasıl** |  |

## Sanctum API Auth Testing

```php
namespace Tests\Feature\Http\Controllers\Api;

use App\Models\User;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Support\Facades\Hash;
use Tests\TestCase;

class AuthControllerTest extends TestCase
{
    use RefreshDatabase;

    public function test_users_can_register(): void
    {
        $response = $this->postJson('/api/register', [
            'name' => 'Test User',
            'email' => 'test@example.com',
            'password' => 'Password123!',
            'password_confirmation' => 'Password123!',
        ]);

        $response->assertCreated();
        $response->assertJsonStructure(['data' => ['user', 'token']]);
    }

    public function test_users_can_login(): void
    {
        User::factory()->create([
            'email' => 'test@example.com',
            'password' => Hash::make('Password123!'),
        ]);

        $response = $this->postJson('/api/login', [
            'email' => 'test@example.com',
            'password' => 'Password123!',
        ]);

        $response->assertOk();
        $response->assertJsonStructure(['data' => ['token']]);
    }

    public function test_users_cannot_login_with_wrong_password(): void
    {
        User::factory()->create(['email' => 'test@example.com']);

        $this->postJson('/api/login', [
            'email' => 'test@example.com',
            'password' => 'wrong',
        ])->assertUnprocessable();
    }

    public function test_token_bearer_authenticates_requests(): void
    {
        $user = User::factory()->create();
        $token = $user->createToken('test')->plainTextToken;

        $this->withToken($token)
            ->getJson('/api/user')
            ->assertOk()
            ->assertJsonPath('data.email', $user->email);
    }
}
```
