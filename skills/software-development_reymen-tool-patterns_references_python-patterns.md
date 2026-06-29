---
name: software-development_reymen-tool-patterns_references_python-patterns
description: Python Kod Kalıpları — beyin.py & guardrails.py Referansı
title: "Software Development Reymen Tool Patterns References Python Patterns"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Python Kod Kalıpları — beyin.py & guardrails.py Referansı |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Python Kod Kalıpları — beyin.py & guardrails.py Referansı

Bu dosya, bu oturumda iyileştirilen `beyin.py` ve `guardrails.py` dosyalarındaki somut kod kalıplarını içerir. `reymen-tool-patterns` skilindeki ana kuralların kanonik örnekleridir.

## beyin.py — Çok Sağlayıcılı LLM Katmanı

### _guvensiz_import() — Tüm Opsiyonel Bağımlılıklar İçin Tek Desen

```python
def _guvensiz_import(modul_adi: str) -> Any:
    """Modülü içe aktar; bulunamazsa None döndür (hata yükseltme)."""
    try:
        import importlib
        return importlib.import_module(modul_adi)
    except ImportError:
        return None

_credential_pool = _guvensiz_import("credential_pool")
_prompt_caching  = _guvensiz_import("prompt_caching")

_POOL_AKTIF  = _credential_pool is not None
_CACHE_AKTIF = _prompt_caching  is not None
```

**Öncesi:** Her opsiyonel modül için ayrı try/except (6 blok)
**Sonrası:** 4 satırda 4 modül, `_AKTIF` flag'ları otomatik

### SaglayiciAdim + LLMYanitMeta — Tip Güvenli Veri

```python
@dataclass
class SaglayiciAdim:
    provider: str
    model: str
    base_url: str
    api_key: str

    def __repr__(self) -> str:
        return f"<SaglayiciAdim provider={self.provider!r} model={self.model!r}>"

@dataclass
class LLMYanitMeta:
    metin: str
    provider: str
    model: str
    sure_sn: float = 0.0
    tahmini_token: int = 0
```

**Öncesi:** Ham `dict` — `adim["provider"]`, `adim.get("model", "...")` — tip denetimi yok
**Sonrası:** `adim.provider`, `adim.model` — IDE otomatik tamamlama, mypy hatasız

### Dispatch Dict — Provider Seçimi

```python
# _cagir() içinde:
dispatch: dict[str, Callable[[], str]] = {
    "lmstudio":           lambda: self._cagir_lmstudio(...),
    "anthropic":          lambda: self._cagir_anthropic(...),
    "moonshot":           lambda: self._cagir_moonshot(...),
    "azure":              lambda: self._cagir_azure(...),
    "bedrock":            lambda: self._cagir_bedrock(...),
    "gemini":             lambda: self._cagir_gemini(...),
    "gemini_cloud":       lambda: self._cagir_gemini(...),
    "lmstudio_reasoning": lambda: self._cagir_lmstudio_reasoning(...),
    "codex_responses":    lambda: self._cagir_codex_responses(...),
}

fn = dispatch.get(
    adim.provider,
    lambda: self._cagir_openai_uyumlu(...),  # varsayılan
)
metin = fn()
```

**Öncesi:** 10 dallı if/elif zinciri
**Sonrası:** 1 dict lookup + 1 call — yeni provider eklemek için 1 satır

### time.monotonic() — Süre Ölçümü

```python
t0 = time.monotonic()
# ... API çağrısı ...
sure = time.monotonic() - t0  # asla negatif olmaz
```

**time.time()** Windows saat değişikliğinde (NTP sync, daylight saving) negatif süre verebilir. `monotonic()` her zaman ileri gider.

## guardrails.py — Hallüsinasyon Filtresi + HITL Sıkılaştırma

### Frozen Dataclass — Uyari

```python
@dataclass(frozen=True)
class Uyari:
    kod: str      # "EMIN_OLMAYAN"
    mesaj: str    # "Yanıt belirsiz/emin olmayan dil içeriyor..."
    skor: float   # 0.5

    def __str__(self) -> str:
        return f"[Guardrail:{self.kod}] {self.mesaj}"
```

**Öncesi:** `list[str]` — uyarılar sadece metindi, kimlik/skor yoktu
**Sonrası:** `list[Uyari]` — makine tarafından okunabilir, filtrelenebilir, toplanabilir

### Ayrı Kontrol Metodları

```python
class HallucinationFiltresi:
    def filtrele(self, yanit, hedef="") -> tuple[str, list[Uyari]]:
        self._toplam_kontrol += 1
        uyarilar: list[Uyari] = []
        uyarilar.extend(self._emin_olmayan_kontrol(yanit))
        uyarilar.extend(self._kesin_iddia_kontrol(yanit))
        uyarilar.extend(self._yanlis_surum_kontrol(yanit))
        uyarilar.extend(self._oz_referans_kontrol(yanit))
        uyarilar.extend(self._uzun_yanit_kontrol(yanit))
        uyarilar.extend(self._iliski_kontrol(yanit, hedef))
        ...
        return yanit, uyarilar

    def _emin_olmayan_kontrol(self, yanit) -> list[Uyari]:
        if _EMIN_OLMAYAN_RE.search(yanit):
            return [Uyari(kod="EMIN_OLMAYAN", ..., skor=0.5)]
        return []  # her zaman list döndür — extend() ile uyumlu
```

**Öncesi:** 6 farklı kontrol `filtrele()` içinde düz, yeni kontrol eklemek için metodu değiştir
**Sonrası:** `filtrele()`'de 1 satır ekle = yeni kontrol, her kontrol bağımsız test edilebilir

### frozenset — Değişmez Sabit Küme

```python
# Modül seviyesinde, asla değişmez
_EK_RISKLI_ARACLAR: frozenset[str] = frozenset({
    "DOSYA_YAZ",
    "TARAYICI_AC",
    "WEB_ARA",
    "TELEGRAM_GONDER",
    "GORUNTU_ANALIZ",
})
```

**Öncesi:** `set` — kazara `.add()` veya `.clear()` yapılabilir
**Sonrası:** `frozenset` — immutable, mypy/hata koruması

### @property — Getter Yöntemi Yerine

```python
class HITLSikistirici:
    @property
    def aktif(self) -> bool:
        return self._aktif

    # Geriye dönük uyumluluk
    def aktif_mi(self) -> bool:
        return self._aktif
```

Kullanım: `if hitl.aktif:` — parantezsiz, doğal özellik erişimi.

### Logging — Detay Seviyesi Kontrolü

```python
logger.debug("[HITL] Zaten sıkılaştırılmış, tekrar çağrı görmezden gelindi.")
logger.warning("[HITL] Motor tanımlı değil; sıkılaştırma atlandı.")
logger.info("[HITL] Sıkılaştırıldı: %d araç onaya eklendi.", len(self._ek_araclar))
```

`print()` her zaman görünür. `logging` ile `--verbose` / `--quiet` kontrolü mümkün.

## Özet: Değişim Metrikleri

| Dosya | Öncesi | Sonrası | Kazanım |
|-------|--------|---------|---------|
| beyin.py | 567 satır, if/elif zinciri, 6 try/except, 5 print() | 964 satır, dispatch dict, 1 _guvensiz_import, logging, tam tip | Daha yavaş çalışır ama daha güvenli, daha genişletilebilir |
| guardrails.py | 248 satır, `sikilaştir()` (ş'li), list[str] uyarı, print() | 363 satır, `sikilas()`, Uyari dataclass, ayrı metodlar, frozenset, logging | Tip güvenli, kolay test, kolay genişletme |
