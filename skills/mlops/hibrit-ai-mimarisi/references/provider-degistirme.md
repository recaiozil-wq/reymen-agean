---
skill_id: 941211bf8077
usage_count: 1
last_used: 2026-06-16
---
# Provider Değiştirme Rehberi

## OpenRouter → Direkt API (Örn: DeepSeek)

OpenRouter üzerinden model kullanmak proxy komisyonu nedeniyle daha pahalıdır.
DeepSeek direkt API'ye geçmek için:

### 1. API Key'i Al
- DeepSeek: https://platform.deepseek.com/
- Hesap aç → API keys → yeni key oluştur
- DeepSeek yeni hesaplara 10M token ücretsiz verir

### 2. ReYMeN Config'e Ekle
```bash
# Provider tanımla
hermes config set providers.deepseek.api_key "sk-..."
hermes config set providers.deepseek.base_url "https://api.deepseek.com/v1"

# Model ve provider'ı aktif et
hermes config set model.default "deepseek/deepseek-chat"
hermes config set model.provider "deepseek"
```

### 3. Doğrula
```bash
hermes config show | grep -E "model|provider|deepseek"
```

Beklenen çıktı:
```
Model: {'provider': 'deepseek', 'default': 'deepseek/deepseek-chat'}
```

### 4. Yeni Oturumda Etkili Olur
Mevcut oturumda eski provider çalışmaya devam eder.
Yeni oturum için `/new` yazılır.

## Fiyat Karşılaştırması

| Model | OpenRouter (nous) | DeepSeek Direkt |
|-------|------------------|-----------------|
| deepseek-chat (giriş) | ~$0.50/1M | $0.27/1M |
| deepseek-chat (çıkış) | ~$1.50/1M | $1.10/1M |
| $0.10 cap ile sorgu | ~20-50 | ~500-1000+ |

## Bilinen Provider'lar

| Provider | Base URL | API Key Formatı |
|----------|----------|-----------------|
| DeepSeek | https://api.deepseek.com/v1 | sk-... |
| OpenAI | https://api.openai.com/v1 | sk-... |
| OpenRouter | https://openrouter.ai/api/v1 | sk-or-... |
| Ollama (yerel) | http://localhost:11434/v1 | ollama (fake) |
