---
name: ecc_laravel-security_references_queue-security
description: Queue Security
title: "Ecc Laravel Security References Queue Security"
version: 1.0.0
---

| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** |  |
| **Nerede** | `AI_ML/ecc_laravel-security_references_queue-security.md` |
| **Ne Zaman** |  |
| **Neden** |  |
| **Nasıl** |  |

## Queue Security

```php
// Define a named rate limiter (typically in AppServiceProvider::boot())
RateLimiter::for('payments', fn () => Limit::perMinute(5));
```

```php
// Encrypt sensitive job data by implementing the interface
final class ProcessPaymentJob implements ShouldQueue, ShouldBeEncrypted
{
    use Dispatchable, InteractsWithQueue, Queueable, SerializesModels;

    public function __construct(
        private readonly string $paymentIntentId, // Public IDs are fine
        private readonly string $cardFingerprint, // Encrypted via ShouldBeEncrypted
    ) {}

    public function handle(): void
    {
        // Process payment
    }

    // Limit retries and delay between attempts
    public function retryUntil(): Carbon
    {
        return now()->addMinutes(5);
    }

    // Rate limit how many jobs of this type can run
    public function middleware(): array
    {
        return [
            new RateLimited('payments'),
        ];
    }
}
```
