---
name: ecc_agent-introspection-debugging_references_stratejik-ajan-secici
description: Stratejik Ajan Seçici (Error-Based Persona Switching)
title: "Ecc Agent Introspection Debugging References Stratejik Ajan Secici"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Stratejik Ajan Seçici (Error-Based Persona Switching) |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Stratejik Ajan Seçici (Error-Based Persona Switching)

## Ne İşe Yarar
LLM çağrısı yapmadan, hata mesajını string analizi ile analiz ederek en uygun ajan personasını seçer. 30+ hata desenini tanır, milisaniyelerde karar verir.

## Kullanım Şekli
```python
from akilli_yonlendirici import stratejik_ajan_sec, ajan_talimatini_getir

# Circuit breaker içinde:
yeni_ajan = stratejik_ajan_sec(aktif_ajan_id, gozlem)
if yeni_ajan != aktif_ajan_id:
    aktif_ajan_id = yeni_ajan
    mesajlar.append({"role": "user", "content": f"[SISTEM]: Yeni rol:\n{ajan_talimatini_getir(aktif_ajan_id)}"})
    ardisik_hata = 1
    continue
```

## 5 Persona ve Hata Desenleri

| Persona | Tetikleyen Hatalar |
|---------|-------------------|
| `kod_uzmani` | SyntaxError, TypeError, NameError, AttributeError, ImportError, ModuleNotFoundError, ValueError, KeyError, IndexError, Traceback |
| `sistem_mimari` | FileNotFoundError, ConnectionError, Timeout, PermissionError, API key, connection refused, broken pipe, no such file |
| `guvenlik_uzmani` | Authentication, Authorization, Forbidden, Unauthorized, invalid token, credentials, SSL, rate limit |
| `veri_uzmani` | Database, SQLite, JSON decode, YAML, encoding, unicode, parsing, CSV |
| `genel_cozucu` | Hiçbiri eşleşmezse (fallback) |

## Avantajları
- LLM maliyeti sıfır (kural tabanlı)
- Milisaniyelerde karar verir
- 30+ hata deseni tanır
- Sistem prompt'una yeni rol enjekte edilir, LLM yeni perspektiften devam eder

## Entegrasyon Noktaları
1. **Circuit Breaker** -> 3 ardışık hatada ajan değiştir, circuit breaker'ı geciktir
2. **Her hata** -> tek hatada ajan değiştir, sıfırla devam et
3. **Maks tur aşımı** -> hangi ajanların denendiğini crash raporuna yaz
