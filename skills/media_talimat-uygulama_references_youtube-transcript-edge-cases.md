
> **Kategori:** Medya

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Tüm ajanlar |
| **Ne?** | Media_Talimat Uygulama_References_Youtube Transcript Edge Cases |
| **Nerede?** | Medya/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

# YouTube Transcript — Edge Cases & Çözümler

## `youtube-transcript-api` sürüm notları

**youtube-transcript-api >= 2.0.0** API değişikliği:

```python
# ESKİ (<=1.x):
from youtube_transcript_api import YouTubeTranscriptApi
t = YouTubeTranscriptApi.get_transcript(video_id)

# YENİ (>=2.0.0):
from youtube_transcript_api import YouTubeTranscriptApi
api = YouTubeTranscriptApi()
t = api.fetch(video_id, languages=['tr', 'en'])
# t.snippets -> [FetchedTranscriptSnippet(text='...', start=0.16, duration=5.599), ...]
```

## Transcript bulunamazsa

1. Önce `--language tr,en` dene
2. Olmazsa `--language en` dene
3. Olmazsa dil belirtmeden dene (herhangi bir dil)
4. Hala yoksa browser ile sayfayı aç, video açıklamasını `meta[name="description"]` ile al
5. Hala yoksa: CC butonu "Subtitles/closed captions unavailable" diyorsa transcript yok demektir

## Tarayıcıdan açıklama alma

```javascript
// Sayfa yüklendikten sonra:
document.querySelector('meta[name="description"]')?.getAttribute('content')
// veya oEmbed API:
https://www.youtube.com/oembed?url=VIDEO_URL&format=json
```

## Tarayıcı sorunları

- YouTube bot detection agresif — browser_snapshot boş dönerse yeniden navigate et
- "more" butonuna tıklamak açıklamayı genişletir ama tüm metni göstermeyebilir
- Meta description genellikle ilk ~150 karakterle sınırlı
