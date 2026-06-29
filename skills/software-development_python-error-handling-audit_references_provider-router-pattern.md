---
name: software-development_python-error-handling-audit_references_provider-router-pattern
description: Provider Router with Circuit Breaker
title: "Software Development Python Error Handling Audit References Provider Router Pattern"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Provider Router with Circuit Breaker |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Provider Router with Circuit Breaker

A reusable architecture for multi-provider LLM setups with automatic failover.

## Architecture

```
User Request
   │
   ▼
Provider Router
   ├── 1. Filter blacklisted providers
   ├── 2. Sort by score (local > fast API > slow API)
   ├── 3. Try each provider in order
   │   ├── Success → report success (reset counter)
   │   └── Fail → report failure → 2 failures = 120s blacklist
   └── 4. All failed → return error message
```

## Components

### Circuit Breaker
- Per-provider failure counter
- 2 consecutive failures → blacklist provider for N seconds (default: 120s)
- Success resets counter
- Thread-safe with `threading.Lock`

### Health Check (Startup Ping)
- Parallel ping all providers via ThreadPoolExecutor (max 6 workers)
- Local providers (LM Studio): GET `/v1/models`
- Remote APIs: GET `/v1/models` with auth header
- 401/403 counts as "alive" (server responds, just needs correct key)
- Timeout: 5s per provider
- Updates provider scores: alive providers get priority

### Smart Sorting
Sort order:
1. Active (not blacklisted) providers first
2. Local providers (LM Studio, Ollama) score highest
3. Mid-range APIs (Groq, Gemini) score medium
4. Ping-alive providers get bonus
5. Fast ping time gives additional bonus

## Key Code Structure

```python
class SaglayiciYonlendirici:
    def kaydet(self, ad: str)              # Register provider for tracking
    def hata_bildir(self, ad: str)          # Report failure (may trigger blacklist)
    def basari_bildir(self, ad: str)        # Report success (resets counter)
    def aktif_mi(self, ad: str) -> bool     # Check if provider is usable
    def sirala(self, zincir: list) -> list  # Smart sort provider chain
    def saglik_kontrolu(self, provider_list) # Parallel ping all providers
    def durum_ozeti(self) -> str            # Human-readable status for /routing command
```

## Integration Points

- **Init:** Register all providers + trigger async health check
- **Each call:** Filter blacklisted providers → sort chain → try in order
- **On success:** `router.basari_bildir(provider)` → reset counter
- **On failure:** `router.hata_bildir(provider)` → increment counter
- **CLI command:** `/routing` shows provider status + fallback chain

## Configuration Constants

| Constant | Default | Meaning |
|----------|---------|---------|
| `_BREAKER_HATA_LIMITI` | 2 | Blacklist after N consecutive failures |
| `_BREAKER_BEKLEME_SN` | 120 | Seconds to stay blacklisted |
| `_PING_TIMEOUT_SN` | 5 | Health check timeout per provider |
| `_LOCAL_PROVIDERS` | lmstudio, ollama | Fast local providers (highest priority) |
| `_KARMA_PROVIDERS` | groq, gemini | Mid-speed API providers |

## See Also

- `python-error-handling-audit` skill — for fixing silent try/except blocks
- `beyin.py` in the project — concrete implementation of `dusun()` with fallback
