---
skill_id: 0e1b427ba5a8
usage_count: 1
last_used: 2026-06-16
---
## Production Configuration

### Essential Production Settings

```php
// config/app.php
'env' => env('APP_ENV', 'production'),
'debug' => (bool) env('APP_DEBUG', false), // CRITICAL: Never true in production
'key' => env('APP_KEY'), // Must be set: php artisan key:generate

// config/session.php
'secure' => env('SESSION_SECURE_COOKIE', true),
'http_only' => true,
'same_site' => 'lax',

// Verify APP_KEY is set at boot
// bootstrap/app.php or a service provider
if (empty(config('app.key'))) {
    throw new RuntimeException('APP_KEY is not set. Run: php artisan key:generate');
}
```

### Environment File Security

```bash