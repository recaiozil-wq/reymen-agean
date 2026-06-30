---
name: autonomous-ai-agents_multi-agent-orchestrator
title: Multi-Agent Orchestrator
description: "Coordinate multiple AI agents for complex task decomposition, parallel execution, and result aggregation."
tags: [agents, orchestration, multi-agent, coordination, task-decomposition]
category: autonomous-ai-agents
audience: agent
---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Tüm ajanlar |
| **Ne?** | Coordinate multiple AI agents for complex task decomposition, parallel execution, and result aggregation. |
| **Nerede?** | autonomous-ai-agents/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

# Multi-Agent Orchestrator

Bu skill, birden çok AI ajanını koordine ederek karmaşık görevleri çözmek için kullanılır.

## 🧩 Mimari

```
Kullanıcı Sorgusu
       │
       ▼
  ┌─────────────┐
  │ Orchestrator │  ← Görevi analiz eder, alt görevlere böler
  └──────┬──────┘
         │
    ┌────┴────┬────┬────┐
    ▼         ▼    ▼    ▼
  Agent_1  Agent_2 ... Agent_N   ← Paralel çalışma
    │         │    │    │
    └────┬────┴────┴────┘
         │
         ▼
  ┌─────────────┐
  │ Aggregator   │  ← Sonuçları birleştirir, çakışmaları çözer
  └──────┬──────┘
         │
         ▼
   Nihai Yanıt
```

## 🔧 Kullanım Adımları

### 1. Görev Analizi

Görevi analiz et ve bağımsız alt görevlere ayır:

1. **Görevi oku**: Kullanıcının isteğini tam olarak anla
2. **Bağımlılıkları belirle**: Hangi adımlar sıralı, hangileri paralel
3. **Alt görev kartları oluştur**: Her alt görev için: {id, aciklama, girdi, beklenen_cikti, bagimlilik}

### 2. Ajan Atama

Her alt görev için uygun ajan seçimi:

| Alt Görev Tipi | Önerilen Ajan | Araçlar |
|----------------|---------------|---------|
| Kod yazma | Code Agent | terminal, write_file, patch |
| Araştırma | Research Agent | web_search, browser |
| Veri analizi | Data Agent | execute_code, terminal |
| Tasarım | Creative Agent | browser, image_gen |
| DevOps | Ops Agent | terminal, docker |

### 3. Paralel Yürütme

```python
# Paralel çalıştırma şablonu
import asyncio
from concurrent.futures import ThreadPoolExecutor

async def parallel_execute(agents, tasks):
    """Birden çok ajanı paralel çalıştır."""
    with ThreadPoolExecutor(max_workers=len(agents)) as pool:
        futures = [pool.submit(agent.run, task) for agent, task in zip(agents, tasks)]
        results = [f.result() for f in futures]
    return results

# Bağımlı görevler için sıralı zincir
def sequential_execute(chain):
    """Bağımlı görevleri sırayla çalıştır."""
    results = []
    for step in chain:
        result = step["agent"].run(step["task"])
        results.append(result)
        # Sonraki adıma bağlam aktar
        if "context" in step and callable(step["context"]):
            step["context"](result)
    return results
```

### 4. Sonuç Birleştirme

Sonuçları birleştirirken:
- **Çakışma tespiti**: Aynı konuda farklı cevaplar varsa doğruluk kontrolü yap
- **Fazlalık temizliği**: Tekrarlanan bilgileri kaldır
- **Tutarlılık sağlama**: Terminoloji ve format tutarlılığını kontrol et
- **Nihai format**: Kullanıcıya sunulacak şekilde yapılandır

## 📋 Komutlar

| Komut | Açıklama |
|-------|----------|
| `orchestrate "görev"` | Görevi analiz et ve ajanları koordine et |
| `orchestrate status` | Çalışan ajanların durumunu göster |
| `orchestrate cancel` | Tüm ajanları durdur |
| `orchestrate retry <agent_id>` | Belirli bir ajanı yeniden çalıştır |

## 🚫 Sınırlamalar

- Maksimum 5 eşzamanlı ajan
- Her ajan için timeout: 300 saniye
- Alt görev sayısı limiti: 10
- Toplam yürütme süresi limiti: 30 dakika
