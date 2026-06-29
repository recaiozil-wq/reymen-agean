---
name: autonomous-ai-agents_checkpoint-onay-sinirlari_references_shim-pattern
description: Shim Pattern — Reymen → Hermes API Redirect
title: "Autonomous Ai Agents Checkpoint Onay Sinirlari References Shim Pattern"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Shim Pattern — Reymen → Hermes API Redirect |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Shim Pattern — Reymen → Hermes API Redirect

## Problem
Reymen testleri (eski API) root'tan import ediyor: `from context_engine import ContextEngine`
Ama modül `agent/context_engine.py`'de (Hermes API). Root'taki eski Reymen
versiyonları silindiği için ModuleNotFound hatası oluşuyor.

## Çözüm: Root Shim Dosyası
Her eksik modül için root'ta yönlendirme shim'i oluştur:

```python
# context_engine.py (root shim)
# -*- coding: utf-8 -*-
from agent.context_engine import *  # noqa: F401, F403
```

## Hangi Modüller İçin Shim Gerekli
Bu session'da oluşturulan shim'ler:
- `context_engine` → agent.context_engine
- `conversation_loop` → agent.conversation_loop
- `tool_guardrails` → agent.tool_guardrails
- `memory_manager` → agent.memory_manager
- `chat_completion_helpers` → agent.chat_completion_helpers
- `memory_provider` → agent.memory_provider
- `display` → agent.display

## Gateway Shim'leri (base.py/helpers.py)
Hermes reference testleri `gateway.platforms.base`'den eksik sınıflar
bekliyor. Bunlar doğrudan base.py'ye eklenmeli (shim değil, stub):

```python
class ProcessingOutcome:
    def __init__(self, status: str = "ok", data: dict = None):
        self.status = status
        self.data = data or {}

class MessageDeduplicator:
    def __init__(self):
        self._seen = set()
    def is_duplicate(self, msg: str) -> bool:
        h = hash(msg)
        if h in self._seen: return True
        self._seen.add(h); return False
```

## Sınırlamalar
- Shim sadece import hatasını çözer. API uyumsuzluğu (farklı sınıf adları,
  farklı parametreler) varsa test yine başarısız olur.
- `*` import polümüz olduğu için namespace kirliliği olabilir. Test
  edilecek ortamda çalıştığından emin ol.
