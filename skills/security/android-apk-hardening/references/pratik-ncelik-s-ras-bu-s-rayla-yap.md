---
skill_id: b84cb30a106d
usage_count: 1
last_used: 2026-06-16
---
## Pratik Öncelik Sırası (Bu Sırayla Yap)

```
1. KRİTİK — Korunan işlevi sunucuya taşı
   Client'ta "premium musun?" sorma, veriyi sunucudan getir.
   Atlanan if, sunucuda olmayan veriyi var edemez.   ❌

2. KRİTİK — Play Integrity sunucuda doğrula
   Nonce sunucuda üret, token sunucuda Google ile çöz.
   Client'ta if'e bağlanmaz, replay-proof.            ❌

3. UCUZ — R8 + imza self-check + dağıtık kontrol
   İmza kontrolünü "tespit et → sunucuya bildir" yap.
   Client'ta karar verirse ⚠️, bildirime çevirince ❌.  ⚠️→❌

4. PAHALI — NDK/native'e taşı
   Son çare. Geliştirme maliyeti en yüksek.
   Ghidra gerekir, caydırıcılık en yüksek.            ⚠️
```

> **Kısa kural:** Client'taki her şey aşılabilir. Gerçek sınır sunucu.
> Önce 1-2'yi kur, sonra 3'ü ekle, 4'ü en sona bırak.

---