
> **Kategori:** Verimlilik

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Tüm ajanlar |
| **Ne?** | Productivity_Memory Compaction_References_Memory Audit Checklist |
| **Nerede?** | Verimlilik/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

# Memory Audit Checklist

## Ne Zaman Kullanılır

Memory doluluğu %90'a ulaşmadan da periyodik kalite audit'i yapmak faydalıdır. Bu checklist, **kapasite analizi** ve **içerik kalite audit'ini** birleştirir.

> **Amaç:** Taşma beklemeden, hafızayı temiz ve verimli tutmak.

## Adım 1: Kapasite Analizi

Mevcut kullanımı sistem prompt'undan oku:

```
MEMORY (your personal notes) [XX% — X,XXX/50,000 chars]
USER PROFILE (who the user is) [XX% — X,XXX/5,000 chars]
```

**Değerlendirme:**
- %0-40 → Kompaksiyon gerekmez, kalite audit'i isteğe bağlı
- %40-70 → Orta doluluk, konsolidasyon düşünülebilir
- %70-90 → Kompaksiyon öncesi hazırlık
- %90+ → Kompaksiyon gerekli (ana SKILL.md'deki adımları izle)

## Adım 2: Mükerrer / Çakışan Kayıt Tespiti

Hafızadaki entry'leri (`§` ile ayrılmış bloklar) tara ve şu kalıpları ara:

| Kalıp | Örnek | Yapılacak |
|-------|-------|-----------|
| Aynı konuda 2+ entry | `.env` hakkında 4 ayrı kayıt | **Konsolide et** → tek entry'de birleştir |
| İç içe geçmiş kurallar | Allow Once x2, Kredi kartı x2 | **Birleştir** → numaralı alt maddeler halinde yaz |
| Aynı yol/bilgi tekrarı | Masaüstü yolu 2 farklı entry'de | **Tek entry** → tüm yolları tek blokta topla |

## Adım 3: Eski / Gereksiz Kayıt Tespiti

Silinecek entry türleri:

- **Oturum özetleri**: "14 Haziran 2026 oturumunda yapılanlar: ..." (session_search ile bulunur)
- **Kurulum bildirimleri**: "X kuruldu", "Y kuruldu, port Z" (çalışıyorsa kalıcı bilgi değil)
- **Tek seferlik analiz sonuçları**: "Skill benchmark yapıldı, skor X" (skill reference'ta duruyor)
- **Geçici durum bildirimleri**: "MCP bridge kuruldu", "cron job oluşturuldu" (zaten çalışıyor)
- **Güncelliğini yitirmiş referanslar**: Eski repo adı, eski kullanıcı adı

**Karar kriteri:** "Bu bilgi olmazsa gelecekte bir işi yapamaz mıyım?"
- Cevap **Evet** → KALDIRILAMAZ (kural, yol, tercih)
- Cevap **Hayır** → SİLİNEBİLİR (bildirim, özet, geçici durum)

## Adım 4: Profil Taşıma

MEMORY'deki kullanıcı tercihlerini tespit et ve USER PROFILE'a taşı:

| MEMORY'de bulunan | USER PROFILE'a taşınacak kısım | MEMORY'de kalacak kısım |
|-------------------|-------------------------------|------------------------|
| "User work style: autonomous..." | Çalışma stili tercihleri | Varsa metodoloji/prosedür bilgisi |
| "User prefers Turkish..." | Dil tercihi, iletişim stili | Ortam bilgileri (yollar, versiyonlar) |
| "User kuralı: soru sorduğumda..." | Bekleme/onay kuralları | (tamamen taşınır) |

**Kural:** MEMORY'deki kullanıcı tercihlerini USER PROFILE'a KOPYALA, ardından MEMORY'den SİL. USER PROFILE'a eklerken mevcut entry'lerle çelişmemeye dikkat et.

## Adım 5: Konsolidasyon Çıktısı

Her konsolide grup için:

```
ESKİ:
Entry A: ... (ilgili konu)
Entry B: ... (aynı konu, farklı detay)
Entry C: ... (üçüncü detay)

YENİ:
BAŞLIK — Kısa özet:
(1) Ana kural veya birinci madde
(2) İkinci madde veya detay
(3) Üçüncü madde
```

## Adım 6: Nihai Rapor

İşlemler bitince şu formatı kullan:

```
Hafıza optimizasyonu tamamlandı.

| Depo | Önce | Sonra | Değişim |
|------|------|-------|---------|
| MEMORY | X / 50,000 (%X) | Y / 50,000 (%Y) | -Z char |
| USER PROFILE | A / 5,000 (%A) | B / 5,000 (%B) | +/-C char |
| Entry sayısı | N entry | M entry | +/-P entry |

Kompaksiyon durumu: Gerekli / Gerekli değil
```

## Güncellenmesi Gereken Skill'ler

Audit sırasında eski limit/sürüm bilgisi tespit edilirse (örn. `memory-compaction` skill'i 10K limitinden bahsediyorken gerçek limit 50K), hemen skill'i de güncelle.
