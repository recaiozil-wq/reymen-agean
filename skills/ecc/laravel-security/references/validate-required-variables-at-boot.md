---
skill_id: 82618e23345d
usage_count: 1
last_used: 2026-06-16
---
# Validate required variables at boot
// In AppServiceProvider::boot()
$requiredKeys = ['app.key', 'database.connections.mysql.database', 'database.connections.mysql.username'];
foreach ($requiredKeys as $key) {
    if (empty(config($key))) {
        throw new RuntimeException("Missing required config key: {$key}");
    }
}
```

### HTTPS Enforcement

```php
// AppServiceProvider::boot() or middleware
if (app()->environment('production')) {
    URL::forceScheme('https');
    request()->server->set('HTTPS', 'on');
}

// config/app.php for trusted proxies (load balancers)
// Use specific IP ranges — * trusts all, allowing X-Forwarded-* spoofing
// AWS: '10.0.0.0/8', '172.16.0.0/12', '192.168.0.0/16'
'trusted_proxies' => ['10.0.0.0/8', '172.16.0.0/12'],

// Force HTTPS in production via middleware
// app/Http/Middleware/ForceHttps.php
public function handle($request, Closure $next)
{
    if (!$request->secure() && app()->environment('production')) {
        return redirect()->secure($request->getRequestUri());
    }
    return $next($request);
}
```