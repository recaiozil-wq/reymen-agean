---
skill_id: fd90ff924b6c
usage_count: 1
last_used: 2026-06-16
---
## 10. Üçüncü Parti AI Video API'leri

MoneyPrinterTurbo **gerçek AI video üretimi yapmaz** — sadece Pexels/Pixabay gibi stok sitelerden hazır videoları bulup birleştirir. "Maymun simit yerken" gibi spesifik sahneler için AI video API'leri gerekir.

### Kling AI

- **Web:** https://kling.ai
- **API:** https://kling.ai/dev/api-key
- **Kayıt:** `.env` → `KLING_ACCESS_KEY`, `KLING_SECRET_KEY`
- **Özellik:** Text-to-video, image-to-video

### RunwayML

- **Web:** https://app.runwayml.com
- **API Docs:** https://docs.dev.runwayml.com/api
- **API Key formatı:** `key_` ile başlayan 128 hex karakter (toplam 132 karakter)
- **Kayıt:** `.env` → `RUNWAYML_API_KEY`
- **API Endpoint:** `api.dev.runwayml.com`
- **Gerekli Header'lar:**
  ```
  Authorization: Bearer <key>
  X-Runway-Version: v1
  ```
- **Not:** API key doğru formatta olsa bile endpoint versiyonu/uyumluluk sorunları olabilir. En güvenilir kullanım web arayüzüdür.

### Manim (3Blue1Brown Matematik Animasyonları)

```bash