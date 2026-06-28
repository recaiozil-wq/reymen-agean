---
skill_id: 39d2e358880d
usage_count: 1
last_used: 2026-06-16
---
## SpeechRecognizer API için Önemli Noktalar
- **İzin:** `RECORD_AUDIO` manifest'te + çalışma zamanında istenmeli
- **Intent extras:** `EXTRA_PARTIAL_RESULTS=true` (kısmi sonuç), `EXTRA_LANGUAGE_MODEL=FREE_FORM`
- **Sürekli dinleme:** `onResults()` callback'inde `startListening()`'i tekrar çağır
- **Hata yönetimi:** `onError()`'da otomatik yeniden başlatma
- **Pitfall:** SpeechRecognizer servisi destroy edilmezse memory leak; `onDestroy()`'da `speechRecognizer.destroy()` çağır