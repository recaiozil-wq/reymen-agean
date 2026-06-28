---
skill_id: aaa9637bbdae
usage_count: 1
last_used: 2026-06-16
---
## Pipeline: Denetimden Sertleştirmeye

```
Adım 0 — jadx ile Java analizi (isPremium nerede?)
    → Kırılganlık haritası oluştur
Adım 1 — apktool ile smali taraması (kaç nokta?)
    → Kontrol sayısını belirle
Adım 2 — String/sabit taraması (API key, flag, endpoint)
    → Hardcode sırları tespit et
Adım 3 — Kırılganlık → Savunma eşleme
    → Her maddeye bir veya daha çok savunma ata
Adım 4 — Sertleştirme uygulama
    → R8 aç, dağıtık kontrol ekle, sunucu doğrulaması kur
Adım 5 — Test: yamala ve dene
    → apktool ile aynı yöntemleri dene, savunma işe yarıyor mu?
```

---