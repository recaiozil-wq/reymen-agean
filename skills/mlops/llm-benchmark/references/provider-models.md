---
skill_id: 6d6f04720abf
usage_count: 1
last_used: 2026-06-16
---
# Provider Model Listelerini Çekme

## Groq
```bash
curl -s "https://api.groq.com/openai/v1/models" \
  -H "Authorization: Bearer $GROQ_API_KEY" | \
  python -c "import sys,json; [print(m['id']) for m in json.load(sys.stdin).get('data',[])]"
```

Aktif modeller (13.06.2026):
- `llama-3.3-70b-versatile` — en sağlam, kod/mantık için
- `meta-llama/llama-4-scout-17b-16e-instruct` — mantıkta iyi (%95)
- `llama-3.1-8b-instant` — çok hızlı ama düşük doğruluk
- `qwen/qwen3-32b` — güvenlik filtresi aşırı hassas
- `groq/compound` — özel model
- `groq/compound-mini` — özel model (küçük)
- `openai/gpt-oss-120b` — OpenAI uyumlu
- `openai/gpt-oss-20b` — OpenAI uyumlu (küçük)
- `allam-2-7b` — Arapça odaklı

**Eski/çalışmayan modeller:**
- ~~`mixtral-8x7b-32768`~~
- ~~`gemma2-9b-it`~~
- ~~`deepseek-r1-distill-llama-70b`~~

**Not:** Groq model adlarını sık değiştirir. Her benchmark öncesi kontrol et.

## DeepSeek
```bash
curl -s "https://api.deepseek.com/v1/models" \
  -H "Authorization: Bearer $DEEPSEEK_API_KEY"
```

Aktif modeller:
- `deepseek-chat` — mevcut, **2026/07/24'te deprecate oluyor**
- `deepseek/deepseek-v4-flash` — yeni ad (eğer API kabul ediyorsa)

## Ollama (yerel)
```bash
ollama list
```
veya
```bash
curl -s http://localhost:11434/api/tags | \
  python -c "import sys,json; [print(m['name']) for m in json.load(sys.stdin).get('models',[])]"
```
