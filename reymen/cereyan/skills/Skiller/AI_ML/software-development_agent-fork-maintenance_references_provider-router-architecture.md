---
name: software-development_agent-fork-maintenance_references_provider-router-architecture
description: Provider Router with Circuit Breaker — Reference Architecture
title: "Software Development Agent Fork Maintenance References Provider Router Architecture"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Provider Router with Circuit Breaker — Reference Architecture |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Provider Router with Circuit Breaker — Reference Architecture

## Core Concept

A `SaglayiciYonlendirici` (Provider Router) sits between the LLM caller layer (`beyin.py`) and the individual provider adapters. It tracks each provider's health state and routes calls intelligently.

```
dusun() → Router.sirala(zincir) → [canlı provider'lar sıralı]
  ↓
  Her provider için:
    ├── router.aktif_mi(provider)? → Hayır → atla
    ├── Başarılı → router.basari_bildir(provider)
    └── Hata → router.hata_bildir(provider) → 2 hata = kara liste 120sn
```

## Data Structures

```python
@dataclass
class SaglayiciDurum:
    ad: str
    hata_sayisi: int = 0
    kara_liste_saati: float = 0.0     # time.monotonic()
    ping_canli: Optional[bool] = None  # None = henüz pinglenmedi
    ping_suresi_sn: float = 0.0
```

## Scoring Algorithm

```python
def sirala(zincir):
    # Yerel providers → ping canlı → hızlı ping süresi
    _LOCAL_PROVIDERS = lmstudio, ollama         # +10 bonus
    _KARMA_PROVIDERS = groq, gemini              # +5 bonus
    ping_canli = +15                             # +15 bonus
    ping_basarisiz = -10                         # -10 ceza
    ping_suresi = max(0, 5.0 - sure)             # hızlı = yüksek skor
```

## Circuit Breaker States

| State | Condition | Behavior |
|-------|-----------|----------|
| Normal | hata_sayisi < 2 | Provider kullanılabilir |
| Blacklisted | hata_sayisi >= 2 | 120sn kara listede, atlanır |
| Recovered | 120sn geçti | Otomatik listeden çıkar |

## Integration Points

### In Beyin.__init__():
```python
self._router = _PROVIDER_ROUTER  # singleton
self._router_kaydet()            # tüm provider'ları kaydet
self._saglik_kontrolu_yap()     # başlangıçta ping
```

### In Beyin.dusun() loop:
```python
# Filter out blacklisted
yerel_zincir = [a for a in yerel_zincir if self._router.aktif_mi(a.provider)]
# Sort optimally
yerel_zincir = self._router.sirala(yerel_zincir)

# Inside try/except for each provider:
# On success:
self._router.basari_bildir(adim.provider)
# On exception:
self._router.hata_bildir(adim.provider)
```

## Health Check

Starts in background thread at agent init:
- Pings each provider's `/v1/models` endpoint
- Local providers (localhost): status==200 → canlı
- API providers: status in (200, 401, 403) → canlı (401/403 = erişilebilir ama yetki sorunu)
- No key / not-needed: skip
- Parallel with ThreadPoolExecutor(max_workers=6)

## CLI Command: `/routing`

Displays:
```
📡 Provider Durumu:
  ✅ deepseek     ping:✅  0.3s
  ✅ groq         ping:✅  0.8s
  ⛔ openai       ping:❌  hata:2  (kara listede, 95s kaldı)
  ✅ lmstudio     ping:✅  0.1s

🔗 Fallback Zinciri:
  1. lmstudio/cognitivecomputations.dolphin3.0-llama3.1-8b
  2. groq/llama-3.1-8b-instant
  3. deepseek/deepseek-v4-flash
```

## Thread Safety

- `threading.Lock` guards all state mutations
- `_durumlar` dict is only modified under lock
- Read operations (`aktif_mi`, `durum_ozeti`) also acquire lock
