---
name: software-development_self-improvement-loop_references_memory-config-pitfalls
description: Memory Config Pitfalls
title: "Software Development Self Improvement Loop References Memory Config Pitfalls"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Memory Config Pitfalls |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Memory Config Pitfalls

## `memory_char_limit` yanlış yerde olabilir

Yaygın hata: `memory_char_limit`'i `general:` altına yazmak.

```
❌ Yanlış:
general:
  memory_char_limit: 50000  # Buradaki değer MemoryStore'a etki etmez!

✅ Doğru:
memory:
  memory_char_limit: 50000   # Gerçek limit burada tanımlanır
  user_char_limit: 25000     # User profile karakter limiti
  max_records: 2000
  dedup_threshold: 0.85
```

## Default değerler
```python
# agent/agent_init.py
memory_char_limit=mem_config.get("memory_char_limit", 2200)  # ~500 kelime
user_char_limit=mem_config.get("user_char_limit", 1375)      # ~300 kelime
```

## Ne kadar yeterli?
- 50K memory + 25K user → aylarca yetecek seviye (günde ~500-1000 karakter yazılıyor)
- 15K → 1-2 haftada dolar (sık temizlik gerekir)
- 100K+ → context şişme riski (her turda bu kadar metin prompt'a eklenir)
