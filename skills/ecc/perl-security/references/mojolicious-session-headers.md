---
skill_id: b9bd1393d845
usage_count: 1
last_used: 2026-06-16
---
# Mojolicious session + headers
$app->secrets(['long-random-secret-rotated-regularly']);
$app->sessions->secure(1);          # HTTPS only
$app->sessions->samesite('Lax');

$app->hook(after_dispatch => sub ($c) {
    $c->res->headers->header('X-Content-Type-Options' => 'nosniff');
    $c->res->headers->header('X-Frame-Options'        => 'DENY');
    $c->res->headers->header('Content-Security-Policy' => "default-src 'self'");
    $c->res->headers->header('Strict-Transport-Security' => 'max-age=31536000; includeSubDomains');
});
```