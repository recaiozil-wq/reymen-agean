---
name: gorev-formati
description: "Kullanıcının istediği 7 maddeli görev formatı — her görevde zorunlu yapı"
category: genel
version: 1.0.0
---

# Görev Formatı (Standart Şablon)

Kullanıcı bir görev verdiğinde, aşağıdaki 7 maddeyi uygula. Şablonu her görevin BAŞINDA zihninde kur.

## 1. GÖREV: [ne yapılacak]
Görevi kullanıcının dilinden tekrar yaz.

## 2. KANIT STANDARDI (zorunlu)
Her adım için ÖZET değil HAM ÇIKTI iste:
- Kod değişikliği → diff veya grep çıktısı
- Test → komutun ham terminal çıktısı
- Dosya oluşturma → ls -la + cat çıktısı
"✅ tamamlandı" yazmak yeterli değil, ham kanıt olmadan kabul edilmez.

## 3. BİTİŞ KRİTERİ (net, sayılabilir)
Görev şu N koşul karşılanınca biter:
1. [koşul 1 + nasıl kanıtlanacağı]
2. [koşul 2 + nasıl kanıtlanacağı]
Hepsi karşılanmadan "tamamlandı" denemez.

## 4. SELF-CHECK ADIMI (en kritik, eksik olan parça)
Tamamladığını düşündüğün anda, KENDİ KENDİNE şunu sor ve cevapla:
"Bu kanıt, başka biri (insan) bağımsızca çalıştırsa AYNI sonucu verir mi? Yoksa sadece benim yorumuma mı dayanıyor?"
Eğer cevap "sadece yorumuma dayanıyor" ise, henüz bitmedi — ham komutu çalıştır, çıktısını kaydet.

## 5. EKSİK KALIRSA (kaçamak yasağı)
X/N koşul karşılanmadıysa, "büyük ölçüde tamamlandı" gibi yumuşatma YASAK. Net yaz: "X/N karşılandı, eksik: [...], sebep: [...]"

## 6. SÜRE/CYCLE SINIRI
Bu görev en fazla [N] cycle içinde bitmeli. Süre dolarsa, nerede kaldığını decisions.md'ye kaydet, durma sebebini yaz.

## 7. KALICI KAYIT (otomatik, görev biter bitmez)
Görev bitince (başarılı ya da eksik), şu üçünü otomatik yap:
- decisions.md'ye sonucu ekle (append ile)
- Eğer tekrar oluşabilecek bir hata kalıbıysa → SKILL.md'ye kural ekle
- Bir sonraki cycle bunu otomatik kontrol etsin diye "doğrulama script'i" varsa, onu cycle başında çalıştırmayı skill'e yaz

## 8. YÜZDE/ORANSAL RAPORLAMA — Metrik/Sağlık Formatı (Kullanıcı Tercihi)

Sağlık/doluluk/metrik raporlarında limit değerlerini **yüzde** cinsinden ifade et:

| Yanlış | Doğru |
|--------|-------|
| `limit = 6000` | `MEMORY_LIMIT_CHARS = 6000  # <%95 doluluk` |
| `limit = 1375` | `USER_LIMIT_CHARS = 6000    # <%95 doluluk` |

Kurallar:
- Limit sabitlerini class seviyesinde tanımla (`MEMORY_LIMIT_CHARS = 6000`)
- Yorum satırında sağlıklı yüzde eşiğini belirt (`# sağlıklı doluluk < %95`)
- Raporda hem karakter sayısını HEM yüzdeyi göster: `"2187/6000 karakter (%36%)"`
- Eşik kontrolü `durum = doluluk < ESIK_YUZDE` ile yap

## 9. SESSİZ ONAY KURALI (akış kontrolü)

Her görev aşaması/adımı sonunda:
1. **Özet ver** (ne yapıldı, sonuç)
2. **3 dakika sessiz bekle** — hiçbir bildirim/sayaç/bekleme yazısı gösterme
3. Cevap gelirse → ona göre devam et
4. 3 dk cevap yoksa → **SESSİZ ONAY** = onay say, sonraki aşamaya geç

## 10. DERİN DEBUG GÖREVİ (özel alt-tip)

"Derin debug" türündeki görevler için 5 aşamalı yapı:
- Aşama 1: **KEŞİF** — oku, değiştirme, tespit et
- Aşama 2: **TANI** — kanıtla, satır numarası göster
- Aşama 3: **DÜZELTME** — izole et, her birini test et
- Aşama 4: **ARAÇ ENTEGRASYONU** — veri kaynağı + cache
- Aşama 5: **TEST & ONAY** — 2 test (ilk + cache hit)

Ayrıntılar için: `skill_view(name="gorev-formati", file_path="references/debug-gorevi.md")`

Kendini geliştirme/debug döngüsü (ADIM 1-6):
`skill_view(name="gorev-formati", file_path="references/kendini-gelistirme-dongusu.md")`

Batch multi-issue fix pattern (N tane bağımsız sorunu aynı anda çözmek için):
`skill_view(name="gorev-formati", file_path="references/batch-multi-issue-fix.md")`

Progress reporting pattern (uzun süreli görevlerde % + beklenti yönetimi):
`skill_view(name="gorev-formati", file_path="references/batch-multi-issue-fix.md")` → Progress Reporting bölümü

## 12. OTURUM BAŞLANGICI — Hafıza Yükle + Raporla (Kullanıcı İsteği)

Her yeni oturumda, kullanıcı ilk mesajı gönderdiğinde (selamlaşma sonrası):

1. **`memory_bank.md`** (veya projenin durum dosyasını) oku — proje kökünde, sistem/ altında veya `.ReYMeN/` içinde olabilir
2. Kullanıcıya şunları söyle:
   - Son ne yapıldı? (git log son commit)
   - Şu an hangi özellikler çalışıyor? (test durumu, hizmetler)
   - Yarım kalan veya bilinen sorun var mı? (önceki oturumdan kalanlar)
3. "Hazırım, devam edebiliriz" de
4. **Kullanıcının onayını almadan hiçbir kod yazma, hiçbir değişiklik yapma**

Bu kural özellikle projeye ilk kez giren AI asistanları için zorunludur. Oturum ortasında gelen yeni görevler için geçerli değildir (sadece yeni oturum açılışında).

## 13. YENİ ÖZELLİK EKLEME — Önce Plan + Onay (Kullanıcı İsteği)

```
[ÖZELLİK]: ...buraya yaz...
```

Kodu yazmadan önce şunları LİSTELE:
1. Hangi dosyalara dokunacaksın? (tam dosya yolları)
2. Bu değişiklik hangi mevcut özellikleri etkileyebilir? (test, import zinciri, config)
3. Risk taşıyan yerler neresi? (veri kaybı, crash, regresyon)

**Kullanıcının onayını aldıktan sonra yaz.** Bitince:
- Ne değiştirdiğini özetle (diff özeti)
- Test etmen gereken eski özellikleri listele (regresyon kontrolü)
- `memory_bank.md`'yi güncelle (veya mevcut durum dosyasını)

Not: Küçük fix'ler (tek satır, %100 güvenli) için bu kural atlanabilir. Sadece anlamlı büyüklükteki özelliklerde uygula.

## 14. BUG DÜZELTİRKEN — Önce Kök Sebep (Kullanıcı İsteği)

```
[BUG]: ...buraya yaz...
```

Düzeltmeden **önce**:
1. Bu bug neden oluşuyor, **kök sebebi** nedir? (satır numarası + teknik açıklama)
2. Düzeltmek için hangi dosyalara dokunacaksın?
3. Bu düzeltme başka neyi bozabilir? (yan etki analizi)

Düzelttikten **sonra**:
- **Testi geçirmek için test kodunu değiştirme** — test doğru, kod yanlış.
- Yaptığın değişikliği satır satır açıkla (neden her satırın değiştiği)
- `memory_bank.md`'yi güncelle

Not: "Hata vs İyileştirme Ayrımı" (kural 11) ile birlikte kullan. Önce BUG mu ENHANCEMENT mı olduğunu belirle.

## 11. HATA vs İYİLEŞTİRME AYRIMI (ZORUNLU — yanılgı önleme)

**KURAL:** Çalışan kodu değiştirmek HATA DEĞİLDİR, İYİLEŞTİRMEDİR.

Tanımlar:
| Tür | Tanım | Örnek | Rapor formatı |
|:----|:------|:------|:--------------|
| **BUG** | Kod **çalışmaz** veya **crash eder** | NameError, ImportError, SyntaxError | `❌ BUG: [dosya] [satır] — [hata]` |
| **ENHANCEMENT** | Kod **çalışıyor** ama daha iyi olabilir | print→log, çıktı temizliği, performans | `⚡ ENHANCE: [dosya] — [ne geliştirdin]` |

Kendine HER DEĞİŞİKLİK ÖNCESİ sor:
1. "Bu kod şu an crash ediyor mu?" → EVET = BUG, HAYIR = ENHANCEMENT
2. "Bu değişiklik olmadan ajan çalışmaz mı?" → EVET = BUG, HAYIR = ENHANCEMENT

**YASAK:** Enhancement'ları "bulunan sorun/hata" gibi sunma. Net ayrım yap:
- "2 bug düzeltildi + 7 enhancement yapıldı" ✅ DOĞRU
- "9 sorun bulundu ve çözüldü" ❌ YANLIŞ (yanıltıcı)
