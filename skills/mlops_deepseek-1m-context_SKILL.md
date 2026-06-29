---
name: deepseek-1m-context
description: Bu skill, DeepSeek'in 1M token context penceresini aktif eder.
title: Deepseek 1M Context
version: 1.0.0
---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | AI/ML mühendisi |
| **Nerede?** | AI_ML/ |
| **Ne Zaman?** | AI/ML görevi gerektiğinde |
| **Neden?** | standardize etmek için |
| **Nasıl?** | Skill adımlarını takip ederek |

ollama_num_ctx=1048576
# DeepSeek 1M Context

Bu skill, DeepSeek'in 1M token context penceresini aktif eder.

## Ne Yapar

config.yaml'de şu değerleri ayarlar:

```yaml
model:
  context_length: 1048576   # 1 milyon token
  ollama_num_ctx: 1048576   # Ollama context boyutu (1M)
```

## Kullanım

### 1. Manuel Kontrol

Config'de değerlerin doğru olduğunu doğrula:

```bash
grep -E "context_length|ollama_num_ctx" ~/AppData/Local/hermes/config.yaml
```

Beklenen çıktı:
```
context_length: 1048576
ollama_num_ctx: 1048576
```

### 2. El İle Ayarla (gerekirse)

```bash
hermes config set model.context_length 1048576
hermes config set model.ollama_num_ctx 1048576
```

### 3. On-Session-Start Hook (Otomatik)

Config her oturumda otomatik kontrol edilir. Eksikse düzeltilir.
Hook script'i: `C:\Users\marko\AppData\Local\hermes\hooks\verify_1m_context.py`

## Önemli

- Bu ayar DeepSeek API üzerinden çalışır (base_url: https://api.deepseek.com/v1)
- `context_length` = model context penceresi (1M token)
- `ollama_num_ctx` = Ollama uyumluluk için aynı değer
- Yeni session açıldığında etkili olur
