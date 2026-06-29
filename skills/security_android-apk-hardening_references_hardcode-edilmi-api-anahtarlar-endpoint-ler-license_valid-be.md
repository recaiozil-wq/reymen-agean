
> **Kategori:** Guvenlik

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Tüm ajanlar |
| **Ne?** | Security_Android Apk Hardening_References_Hardcode Edilmi Api Anahtarlar Endpoint Ler License_Valid Be |
| **Nerede?** | Guvenlik/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

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