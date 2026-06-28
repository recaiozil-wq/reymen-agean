---
name: software-development_reymen-proje-benchmark_references_hermes-reference-test-workflow
description: Hermes Reference Test Workflow
title: "Software Development Reymen Proje Benchmark References Hermes Reference Test Workflow"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Hermes Reference Test Workflow |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Hermes Reference Test Workflow

Reymen projesindeki `tests/hermes_reference/` klasörü, Hermes Agent'tan kopyalanmış **1.555 test dosyası** içerir. Bunların çoğu Hermes'e özel modüller import ettiği için Reymen'de collection error verir.

## Doğru Test Stratejisi

### Hata: Tamamını Tek Seferde Çalıştırmak

```bash
# YANLIŞ — collection error'lar cascade olur, çoğu test koşamaz
python -m pytest tests/hermes_reference/ --tb=line -q
# -> 379 item collected / 373 errors (sadece 6 item koşar)
```

### Doğru: Kategori Kategori Çalıştır

Önce hangi kategorilerin çalıştığını bul:

```bash
python -m pytest tests/hermes_reference/hermes_state/ --tb=line -q
python -m pytest tests/hermes_reference/openviking_plugin/ --tb=line -q
python -m pytest tests/hermes_reference/cron/ --tb=line -q
python -m pytest tests/hermes_reference/website/ --tb=line -q
```

### Collection Error Tespiti

286 dosyada collection error var. Bunlar `--collect-only` + grep ile kategorize edilir:

```bash
python -m pytest tests/hermes_reference/ --collect-only 2>&1 | grep "^ERROR " | sort
```

Kategori dağılımı:
- `hermes_cli/`: 131 dosya (Hermes CLI komutları)
- `agent/`: 45 dosya (transport, lsp, compressor)
- `cli/`: 35 dosya (TUI, status, skin)
- `plugins/`: 32 dosya (memory, image_gen, google_meet)
- `run_agent/`: 13 dosya (guardrails, compression)
- `acp/`: 10 dosya (auth, permissions)
- `docker/`: 6 dosya
- diğer: ~14 dosya

### JUnit XML Sınırlaması

Collection error'ları JUnit XML'de `classname` boş gelir — kategori bazlı gruplama yapılamaz. Bunun yerine `--collect-only` çıktısını `grep "^ERROR "` ile parse et.

### Hata Türleri

| Tür | Örnek | Çözüm |
|-----|-------|-------|
| ImportError | `cannot import name 'COMMAND_REGISTRY'` | Hermes modülü Reymen'de yok |
| ModuleNotFoundError | `No module named 'gateway.platforms.base'` | Paket tamamen eksik |
| AttributeError | `format_runtime_provider_error` | Reymen'de farklı isimlendirme |

### Rapor Formatı (Claude Code İçin)

```
### Kategori: [name]
- Toplam: N test
- ✅ Gecti: N
- ❌ Basarisiz: N
- ⚠️ Hata: N
- Sebep: [kısa açıklama]

En sık hata: `ImportError: cannot import X from Y`
```

### Çalışan Kategoriler (17 Haziran 2026)

| Kategori | Gecti | Basarisiz | Hata |
|----------|-------|-----------|------|
| hermes_state | 31 | 2 | 0 |
| openviking_plugin | 11 | 2 | 0 |
| cron | 264 | 100 | 92 |
| website | 0 | 0 | 20 |

**Toplam:** 306 ✅ / 104 ❌ / 112 ERROR (çalışan kategorilerde)
