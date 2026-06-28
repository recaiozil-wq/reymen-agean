---
skill_id: 477048404101
usage_count: 1
last_used: 2026-06-16
---
## 6. Video Oluşturma (CLI)

### Temel Kullanım

```bash
.venv/Scripts/python.exe cli.py \
  --video-subject "Konu başlığı" \
  --video-source pexels \
  --voice-name "tr-TR-EmelNeural" \
  --no-subtitle-enabled
```

**UYARI:** `--voice-name` zorunludur. Config.toml'daki `voice_name` değeri CLI tarafından OKUNMAZ.

### Parametre Tablosu

| Param | Zorunlu | Açıklama |
|-------|---------|----------|
| `--video-subject` | Evet | Video konusu |
| `--voice-name` | **Evet** | TTS ses adı |
| `--video-source` | Hayır | pexels/pixabay/coverr/local (varsayılan: pexels) |
| `--no-subtitle-enabled` | Hayır | Altyazıyı kapatır |
| `--video-terms` | Hayır | Virgülle ayrılmış Pexels arama terimleri |
| `--video-materials` | local için | Local video yolları (`storage/local_videos/` altında) |
| `--stop-at` | Hayır | script/terms/audio/subtitle/materials/video |
| `--video-count` | Hayır | Kaç video (varsayılan: 1) |

### Özel Arama Terimleri (--video-terms)

DeepSeek'in otomatik term üretmesini beklemeden istediğin sahneleri doğrudan arat:

```bash
--video-terms "blonde woman Istanbul,Galata Tower drone view,dolphin jumping seagulls flying"
```

### Seslendirmesiz Video (No-Voice)

`--voice-name "no-voice"` ile TTS tamamen kapatılır. Sessiz oluşturulur, sadece bgm kalır:

```bash
.venv/Scripts/python.exe cli.py \
  --video-subject "Konu" \
  --video-source pexels \
  --voice-name "no-voice" \
  --no-subtitle-enabled
```

Süre `generate_silent_audio()` tarafından otomatik hesaplanır (~61 sn).

### TTS Ses Sağlayıcıları

| Sağlayıcı | Prefix | API Key Gerekli | Örnek |
|-----------|--------|----------------|-------|
| Edge TTS (ücretsiz) | (yok) | Hayır | `tr-TR-EmelNeural` |
| Azure TTS V2 | `-V2` | `azure_api_key` | `tr-TR-EmelNeural-V2` |
| Gemini TTS | `gemini:` | `gemini_api_key` | `gemini:Zephyr-Female` |

**Türkçe Edge TTS sesleri:** `tr-TR-EmelNeural` (kadın), `tr-TR-AhmetNeural` (erkek)

### Local Video Kullanımı

```bash
--video-materials "C:/Users/marko/MoneyPrinterTurbo/storage/local_videos/video1.mp4"
```

Video dosyaları `storage/local_videos/` altında olmalı (güvenlik kısıtlaması).

### Çıktı

`storage/tasks/<task_id>/final-1.mp4`