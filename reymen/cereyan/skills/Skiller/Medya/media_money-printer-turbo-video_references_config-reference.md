
> **Kategori:** Medya

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Video ajanı |
| **Ne?** | Media_Money Printer Turbo Video_References_Config Reference |
| **Nerede?** | Medya/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

# MoneyPrinterTurbo Config Referansı

## LLM Sağlayıcı Ayarları (config.toml → [app])

| Sağlayıcı | api_key alanı | base_url | model_name |
|-----------|--------------|----------|------------|
| DeepSeek | `deepseek_api_key` | `https://api.deepseek.com` | `deepseek-chat` |
| OpenAI | `openai_api_key` | - | `gpt-4o-mini` |
| AIHubMix | `aihubmix_api_key` | `https://aihubmix.com/v1` | `gpt-5.4-mini` |
| AIML API | `aimlapi_api_key` | `https://api.aimlapi.com/v1` | `openai/gpt-4o-mini` |
| Moonshot | `moonshot_api_key` | `https://api.moonshot.cn/v1` | `moonshot-v1-8k` |
| Ollama | - (boş) | `http://localhost:11434/v1` | `llama3` |
| Google Gemini | `gemini_api_key` | - | `gemini-2.5-flash` |
| Groq | `groq_api_key` | `https://api.groq.com/openai/v1` | `llama-3.3-70b-versatile` |
| Qwen | `qwen_api_key` | - | `qwen-max` |
| MiniMax | `minimax_api_key` | `https://api.minimax.io/v1` | `MiniMax-M3` |
| SiliconFlow | `siliconflow_api_key` | `https://api.siliconflow.cn/v1` | `deepseek-ai/DeepSeek-V3` |
| Azure OpenAI | `azure_api_key` | - | `gpt-35-turbo` |

## Video Kaynağı Ayarları

| Kaynak | API Key Gerekli | Açıklama |
|--------|----------------|----------|
| `local` | HAYIR | Kendi video dosyaların (`storage/local_videos/`) |
| `pexels` | EVET | Ücretsiz stok video (günde limitli) |
| `pixabay` | EVET | Ücretsiz stok video (günde 5000 istek) |
| `coverr` | EVET | Ücretsiz stok video (50 istek/saat demo) |

## Türkçe Edge TTS Sesleri

| Ses Adı | Cinsiyet |
|---------|----------|
| `tr-TR-EmelNeural` | Kadın |
| `tr-TR-AhmetNeural` | Erkek |

Tüm ses listesi: `docs/voice-list.txt`

## CLI Parametreleri

| Parametre | Zorunlu | Açıklama |
|-----------|---------|----------|
| `--video-subject` | EVET | Video konusu |
| `--video-script` | HAYIR | Özel senaryo (boşsa AI üretir) |
| `--video-source` | HAYIR | `pexels`, `pixabay`, `coverr`, `local` (default: pexels) |
| `--video-materials` | HAYIR | Local video dosya yolları (virgülle ayrılır) |
| `--voice-name` | HAYIR | TTS ses adı |
| `--stop-at` | HAYIR | `script`, `terms`, `audio`, `subtitle`, `materials`, `video` |
| `--video-aspect` | HAYIR | `9:16` (dikey) veya `16:9` (yatay) |
| `--video-count` | HAYIR | Kaç video üretileceği (default: 1) |
| `--subtitle-enabled` | HAYIR | Altyazı aç/kapa (default: True) |
