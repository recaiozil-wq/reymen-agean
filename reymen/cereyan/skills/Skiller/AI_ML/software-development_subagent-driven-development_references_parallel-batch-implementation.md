---
name: software-development_subagent-driven-development_references_parallel-batch-implementation
description: Parallel Batch Implementation — Case Study
title: "Software Development Subagent Driven Development References Parallel Batch Implementation"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Parallel Batch Implementation — Case Study |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Parallel Batch Implementation — Case Study

Bu reference, `subagent-driven-development` skill'ini genişleten bir desendir:
**çoklu bağımsız dosyanın paralel subagent'larla oluşturulması**.

## Ne Zaman Kullanılır

- 10+ dosyanın aynı pattern'da oluşturulması gerektiğinde
- Dosyalar birbirine bağımlı DEĞİLSE (her biri bağımsız)
- Her dosya aynı template'i takip ediyorsa
- Hız kritikse (3x paralel hızlanma)

## Ne Zaman KULLANILMAZ

- Dosyalar birbirine bağımlıysa (A olmadan B çalışmaz)
- Önce analiz/plan gerekiyorsa
- Karmaşık entegrasyon adımları varsa

## Desen

### Adım 1: Task'leri Böl

3 paralel task, her biri 3-7 bağımsız dosya:

```
delegate_task(
  goal = "Create 5 tools: A, B, C, D, E",
  context = "Proje yolu, pattern, stil kuralları, mevcut kod örnekleri",
  toolsets = ["terminal", "file"]
)
```

**Her task'ın context'ine şunları koy:**
- Hedef proje yolu (tam mutlak yol)
- Template/shadow kod (mevcut bir tool'un kodu, örnek olsun diye)
- Stil kuralları (docstring, try/except, hangi dil)
- Benzersizlik vurgusu ("Hermes kopyası değil, X kimliğine uygun")
- Dosyaların tam listesi ve her birinin ne yapacağı

### Adım 2: Her Subagent Kendi İşini Yapar

Her subagent:
1. `write_file` ile her dosyayı yazar
2. `python -c "import modul; print('OK')"` ile import testi yapar
3. Özet döndürür

### Adım 3: Sonuçları Birleştir

Sonuçları topla, eksik/başarısız varsa not et, toplam metrik göster.

## Örnek: 17 Tool + 7 Gateway + 5 Transport (Bu Oturum)

Bu oturumda 3 paralel subagent × 8 batch = 29 yeni dosya oluşturuldu:

| Batch | Subagent 1 | Subagent 2 | Subagent 3 |
|-------|-----------|-----------|-----------|
| 1 | 5 tool | 5 tool | 3 tool |
| 2 | 4 tool | 7 gateway | — |
| 3 | 5 gateway | 5 transport + 2 tool | — |
| 4 | 3 memory + 4 test + motor güncelleme | — | — |

Toplam: 40 tool, 28 gateway, 5 transport, 3 memory plugin, 3 test dosyası
Süre: ~20 dakika (sıralı yapsaydı ~60 dk olurdu)

## Pitfalls

1. **Context'i detaylı ver** — Subagent'ın senin geçmiş oturumundan haberi yok. Hangi pattern'ı kullanacağını, hangi projede çalıştığını, dil tercihlerini açıkça belirt.
2. **Her subagent'a template kod ver** — "Şu pattern'ı takip et" demek yetmez, mevcut bir dosyanın kodunu göster ki tutarlı olsun.
3. **Import testi yaptır** — Subagent işini bitirince "her dosya import edilebiliyor mu" kontrolünü yaptır. Yoksa boş/kırık dosya gelebilir.
4. **Entegrasyonu ayrı yap** — Subagent'lar dosyayı yazar, import testini yapar. Entegrasyon (motor.py'ye ekleme, __init__.py güncelleme) ANA AJAN tarafından yapılır, subagent'a bırakılmaz.
5. **3'ten fazla paralel task açma** — Bu kullanıcı için max 3 paralel. 4. task beklemeye alınır.
