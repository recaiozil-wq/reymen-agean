---
skill_id: b61aa8ecb17c
usage_count: 1
last_used: 2026-06-16
---
# Fallback Provider Yapılandırması

## Sorun
DeepSeek API kredisi bittiğinde `fallback_providers: []` olduğu için ReYMeN çalışmayı durdurur. 
`api_max_retries: 3` ile her mesajda 3 kere DeepSeek'e gider, her seferinde "insufficient_quota" hatası alır.
Kredi düşmez ama request'ler boşuna gidip gelir.

## Çözüm
Bir fallback provider ekle (örn. LM Studio'daki Dolphin/Qwen modeli):

```yaml
# config.yaml
fallback_providers:
  - provider: custom
    model: cognitivecomputations.dolphin3.0-llama3.1-8b
    base_url: http://localhost:1234/v1
    api_key: ""
```

Veya hibrit AI sağlık kontrolü cron'una fallback testi ekle:
1. DeepSeek API'ye test isteği at
2. Başarısızsa → LM Studio modeline geç
3. Kullanıcıya bildirim gönder

## Not
- Ollama KALDIRILDI — LM Studio tercih edilen local LLM
- LM Studio portu: localhost:1234
- Mevcut modeller: qwen3-32b, dolphin3.0-8b, llava-v1.6 (vision)
