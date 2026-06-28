---
skill_id: d34bf3595548
usage_count: 1
last_used: 2026-06-16
---
# "Sorma" Workflow — Doğrudan Uygulama Deseni

Bu kullanıcı için en kritik kural: **sorma, yap.**

## Ne Zaman Uygulanır

- Kullanıcı bir eksik listesi veya yapılacaklar listesi verdiğinde
- Kullanıcı "sorma", "atla", "yap gitsin", "sen karar ver" dediğinde
- Kullanıcı "nasıl yapayım" gibi bir ifade kullandığında (bu "sen karar ver" anlamına gelir)
- Kullanıcı "devam" dediğinde — hiçbir şey sorma, kaldığın yerden devam et

## Adımlar

1. **Tüm listeyi oku**, anlamadığın bir madde varsa tahmin et — sorma
2. **En kritikten başla** (çalışmayı engelleyenler önce)
3. **Arkada çalıştır** mümkünse — `terminal(background=true)`
4. **Her adımda bildirim gönderme** — bitince tek seferde özet ver
5. **Hata varsa düzelt ve devam et** — kullanıcıya bildirme, çözüm üret
6. **Sonunda tablo ver** — ne yapıldı, ne kaldı

## Kritik: "Sadece Tamam De" Kuralı (≥ v3)

Kullanıcı uzun bir oturumda "devam" dediğinde veya eksik listesi verdiğinde:

1. **Tüm batch bitene kadar HİÇBİR ŞEY söyleme**
2. Ara adım soruları sorma ("bunu mu yapayım?", "şimdi ne yapayım?", "bu iyi mi?")
3. Ara raporlar verme ("X yapıldı, sırada Y var")
4. Her batch bitince sadece ✅/❌ göster, yorum yapma
5. **TÜM İŞ BİTİNCE** sadece "tamam" yaz, bekle
6. Açıklama, özet, detay istemezse ekleme — sadece "tamam"

Bu kuralın ihlali = kullanıcının "neden her defasında ilerleme onay istiyorsun" demesiyle sonuçlanır.

**Örnek doğru davranış:**
```
Kullanıcı: "devam"
Sen: [sessizce çalış, 15 dosya oluştur, test et, entegre et]
Sen: [hiçbir şey sorma, hiçbir ara mesaj gönderme]
Sen: "tamam"
```

**Örnek yanlış davranış:**
```
Kullanıcı: "devam"
Sen: "X dosyasını yazdım, şimdi Y'yi entegre edeyim mi?"  ← YANLIŞ
Sen: "3/12 tamam, kalan 9 dosya..."                          ← YANLIŞ
Sen: "bunu mu önce yapayım yoksa şunu mu?"                   ← YANLIŞ
```

## Tuzaklar

- **Aşırı detay**: Her adımı açıklama. Kullanıcı "kısaca anlat" veya "yeter" derse 3 cümleyi geçme.
- **Onay beklemek**: "Şunu yapayım mı?" diye sorma. En mantıklı kararı ver ve yap.
- **Sıra sormak**: Önce çalışmayı engelleyen kritik hatayı bul, onu düzelt, sonra diğerlerini.
- **Ara rapor vermek**: "X yapıldı, kaldı Y" gibi ara mesajlar gönderme. Kullanıcı istemiyor. Sadece iş bitince tek mesaj.
- **Uzun oturumda konuşkanlık**: 5+ batch'lik işte her batch sonu "sıradaki batch'e geçiyorum" deme. Sessizce geç.
