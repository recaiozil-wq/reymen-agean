---
name: ecc_laravel-security_references_validate-secrets-at-boot-appserviceprovider-boot
description: Validate secrets at boot (AppServiceProvider::boot)
title: "Ecc Laravel Security References Validate Secrets At Boot Appserviceprovider Boot"
version: 1.0.0
---

| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** |  |
| **Nerede** | `AI_ML/ecc_laravel-security_references_validate-secrets-at-boot-appserviceprovider-boot.md` |
| **Ne Zaman** |  |
| **Neden** |  |
| **Nasıl** |  |

# Validate secrets at boot (AppServiceProvider::boot)
$secrets = ['services.stripe.key', 'services.stripe.webhook_secret'];
foreach ($secrets as $key) {
    if (empty(config($key))) {
        Log::critical("Missing secret: {$key}");
    }
}
```
