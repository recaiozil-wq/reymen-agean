---
skill_id: 1fa0996cbe33
usage_count: 1
last_used: 2026-06-16
---
# Tekrar imzala (birleştirme imzayı bozar)
apksigner sign --ks my.keystore --ks-key-alias myalias monolithic.apk
```

Veya manifest'ten split referanslarını temizle, `apktool b` ile yeniden build et.

#### 8. Doğrula
```bash