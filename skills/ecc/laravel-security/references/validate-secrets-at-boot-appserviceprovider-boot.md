---
skill_id: 76b76f2cf464
usage_count: 1
last_used: 2026-06-16
---
# Validate secrets at boot (AppServiceProvider::boot)
$secrets = ['services.stripe.key', 'services.stripe.webhook_secret'];
foreach ($secrets as $key) {
    if (empty(config($key))) {
        Log::critical("Missing secret: {$key}");
    }
}
```