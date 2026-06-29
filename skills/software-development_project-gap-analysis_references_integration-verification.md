---
name: software-development_project-gap-analysis_references_integration-verification
description: Entegrasyon Dogrulama
title: "Software Development Project Gap Analysis References Integration Verification"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Entegrasyon Dogrulama |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Entegrasyon Dogrulama

## Ne Zaman Kullanilir

Her yeni dosya/modul olusturuldugunda, ana sisteme baglanmasi
icin bu kontrol listesini uygula.

## Entegrasyon Matrisi

Batch'e baslamadan once su matrisi cikar:

```
Yeni Dosya             → Hedef Dosya (Import)            → Kullanim Sekli
────────────────────────────────────────────────────────────────────────────
iteration_budget.py    → main.py                         → AIAgentOrchestrator.budget
prompt_builder.py      → main.py                         → AIAgentOrchestrator.prompt_builder
trajectory.py          → main.py                         → AIAgentOrchestrator.trajectory
credential_pool.py     → beyin.py + main.py              → _anahtar_bul()
prompt_caching.py      → beyin.py                        → cache_ile_uret()
nous_rate_guard.py     → beyin.py                        → rate_guard_izin_ver()
tools/*.py             → motor.py (registry)             → tool_registry.calistir()
gateway/platforms/*    → gateway_runner.py               → platform_listele()
```

## Entegrasyon Adimlari (Her Dosya Icin)

### 1. IMPORT EKLE

Hedef dosyaya import satiri ekle:

```python
# Hedef: motor.py
try:
    from file_safety import guvenli_mi
    _FILE_SAFETY_AKTIF = True
except ImportError:
    _FILE_SAFETY_AKTIF = False
```

Her zaman try/except kullan (graceful degrade).

### 2. INITIALIZE

Ana sinifin `__init__` metodunda nesneyi olustur:

```python
try:
    from iteration_budget import IterationBudget
except ImportError:
    IterationBudget = None

class AIAgentOrchestrator:
    def __init__(self, ...):
        self.budget = IterationBudget(max_tur=max_tur) if IterationBudget else None
```

### 3. KULLAN

Ana dongude yeni modulu cagir:

```python
# main.py - run_conversation
if self.budget:
    self.budget.tur_basla()
    if not self.budget.devam_etmeli_mi():
        break
```

### 4. TEST ET

Import ve calisma testi:

```bash
# Import testi
python -c "from motor import Motor; print('OK')"

# Entegrasyon testi
python -c "
from main import AIAgentOrchestrator, CONFIG
agent = AIAgentOrchestrator(config=CONFIG, max_tur=2)
print(f'Budget: {agent.budget is not None}')
"
```

## Kontrol Listesi

```
[ ] Dosya yazildi (syntax hatasiz)
[ ] Hedef sisteme import edildi (try/except ile)
[ ] Ana sinifta initialize edildi
[ ] Ana dongude kullanildi
[ ] Import testi gecti (0 hata)
[ ] Basit calisma testi gecti
```

## Yaygin Entegrasyon Desenleri

| Desen | Kod |
|-------|-----|
| try/except import | `try: from X import Y; _AKTIF = True except: _AKTIF = False` |
| Opsiyonel init | `self.x = X() if X else None` |
| Guard kullanimi | `if self.x: self.x.islem_yap()` |
| tool_registry | `self._registry.kaydet("AD", fonk)` |
| global instance | `_pool = CredentialPool()` (modul seviyesinde) |
