
> **Kategori:** Guvenlik

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Tüm ajanlar |
| **Ne?** | Security_Android Apk Hardening_References_K R Lganl K Haritas Savunma E Leme Tablosu Ncelik S Ral |
| **Nerede?** | Guvenlik/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

## Kırılganlık Haritası → Savunma Eşleme Tablosu (Öncelik Sıralı)

| Öncelik | Kırılganlık | Savunma | Etki |
|---------|-------------|---------|------|
| **1 — KRİTİK** | Premium kararı client'ta boolean | Korunan işlevin verisini sunucuya taşı, client'ta karar verme | ❌ Atlanan if, sunucuda olmayan veriyi var edemez |
| **2 — KRİTİK** | Play Integrity verdict'i client'ta doğrulanıyor | Nonce sunucuda üret, token'ı sunucuda Google ile çöz | ❌ Client'ta if'e bağlı değil, replay-proof |
| **3 — UCUZ** | jadx ile okunabilir kod | R8/ProGuard obfuscation | ⚠️ Caydırıcı, okumayı zorlaştırır |
| **4 — UCUZ** | İmza kontrolü yok | İmza self-check + **sunucuya bildir** (karar verme) | ❌ `if (!imzaOk) { sunucuyaBildir() }` — karar client'ta değil |
| **5 — UCUZ** | Tek noktadan karar | Dağıtık kontrol (3+ nokta) | ⚠️ Çıtayı yükseltir, hepsi bulunana kadar korur |
| **6 — PAHALI** | Java'da lisans mantığı | NDK/native'e taşı (Ghidra gerekir) | ⚠️ En yüksek maliyet, son çare |

### Özet — Tablonun Tek Cümlelik Dersi

> Client'taki her şey aşılabilir. Gerçek güvenlik sınırın sunucu.
> Client tarafı sadece geciktirme katmanıdır.

### Nihai Sonuç — Yama Yapılamaz Tasarım

Server-yetkilendirmeli tasarımda APK yaması ölü yol:
- Cihazda atlanacak karar yok: `isPremium()` boolean'ı yok, `if-eqz` yok
- Korunan veri cihazda değil, sunucuda üretiliyor
- APK yamalanıp imzalansa bile sunucu "yetkili değilsin" der
- Saldırı yüzeyi "herkes yamalayabilir"den "geçerli hesap gerekir"e kayar

Kalan riskler APK zafiyeti değil, standart auth sorunları:
- Hesap paylaşımı → cihaz başına oturum, eşzamanlı oturum limiti
- Hesap ele geçirme → MFA, token binding, şüpheli giriş tespiti

---