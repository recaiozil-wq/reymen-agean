
> **Kategori:** Verimlilik

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Tüm ajanlar |
| **Ne?** | Productivity_Agent Conduct Framework_References_Youtube Apply Workflow |
| **Nerede?** | Verimlilik/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

# YouTube Video → Uygulama İş Akışı

Kullanıcı bir YouTube URL'si paylaştığında videodaki talimatları çıkar, uygula ve karar döngüsüne kaydet.

## Akış

1. **Transcript al** — `youtube_transcript_api` ile:
   ```python
   from youtube_transcript_api import YouTubeTranscriptApi
   api = YouTubeTranscriptApi()
   t = api.fetch('VIDEO_ID', languages=['tr', 'en'])
   ```
   Önce `tr,en` dene, olmazsa `en` dene, olmazsa dili belirtmeden dene.

2. **Talimatları çıkar** — Transcript'teki:
   - Kurulum adımları (install, download, configure)
   - Kod parçaları
   - Yapılandırma değişiklikleri
   - Önemli uyarılar (path'te çift backslash gibi)

3. **Uygula** — Terminal ile:
   - Paket kurulumu
   - Dosya/config düzenleme
   - Doğrulama (exe var mı, config geçerli mi)

4. **Karar Döngüsü'ne kaydet** — `.ReYMeN/decisions.md`'ye:
   - Ne yapıldı?
   - Neden?
   - Alternatif düşünüldü mü?
   - Durum tablosu (✅ / ⏳ / ❌)

## Transcript Yoksa

Eğer `youtube_transcript_api` transcript bulamazsa:
1. Browser ile video sayfasını aç
2. `meta[name="description"]` ve `og:description`'dan açıklamayı al
3. Videodaki chapter/timestamp listesini çıkar
4. Kullanıcıya "Transcript yok, açıklamadan ilerliyorum" de

## Önemli Uyarılar

- Windows path'lerinde **çift backslash** (`\\`) kullan (video'da belirtilmiş olabilir)
- VS Code extension'ları `.vscode/extensions/` altında
- Microsoft Store uygulamaları `winget` ile yönetilir
- Config değişikliklerinden sonra YAML doğrulaması yap
