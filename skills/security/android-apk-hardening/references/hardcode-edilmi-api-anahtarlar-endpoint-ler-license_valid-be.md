---
skill_id: 78408dc7c886
usage_count: 1
last_used: 2026-06-16
---
# Hardcode edilmiş API anahtarları, endpoint'ler, "license_valid" benzeri flag string'leri
strings app.apk | grep -i "api\|key\|secret\|token\|license\|premium\|https://" | head -20
```

Bunlar:
- Saldırgana harita verir (hangi endpoint, hangi parametre)
- Hardcode edilmiş sırların sızması demektir
- `license_valid`, `is_premium` gibi açık string sabitleri gömülüyse, doğrudan hedef gösterir

### 1d — Kırılganlık Haritası Çıktısı

Faz 1'in çıktısı şu cümleleri kurabilmek olmalı:

```
ÖRNEK: "Premium kararım client tarafında, tek boolean (isPremium),
SharedPreferences'ta 'premium_unlocked' anahtarıyla saklanıyor,
sunucu hiç sormuyor. if-eqz → if-nez yamasıyla 30 saniyede kırılır."
```

Bu cümleyi kurabiliyorsan zaafiyet net.

---