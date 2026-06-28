---
skill_id: 10e25db8a6b0
usage_count: 1
last_used: 2026-06-16
---
# Claude Code Test Dosyasi Temizligi

## Problem

Claude Code, projeyi analiz ederken kendi kendine test dosyalari olusturur:
- `test_bulk_*.py` — 1000+ satirlik `assert 0+1==1` gibi anlamsiz testler
- `test_gen_*.py` — `tools.var_olmayan_modul` gibi import edilemeyen tool'lari test eder
- `test_tools_*.py`, `test_browser_*.py` vb. — var olmayan modullere referans verir

Bu dosyalar:
- pytest'i dakikalarca asili birakabilir (import edilemeyen modul)
- 25.000+ satir gereksiz kod ekler
- Gecersiz import'larla test suite'ini kirar
- Claude Code bunlari kendiliginden temizlemez

## Cozum

Her Claude Code calismasindan sonra su dosyalari kontrol et ve sil:

```bash
# Bulk test dosyalari (anlamsiz assert'ler)
rm -f tests/test_bulk*.py

# Genere edilmis test dosyalari (import edilemeyen tool'lar)
rm -f tests/test_gen_*.py

# Claude Code tarafindan olusturulmus test uretecleri
rm -f tests/generate_tests.py tests/son_push.py
```

## Guvenli Testler

Sadece su test dosyalarini koru (elle yazilmis, calisir durumda):
- `test_core.py` — cekirdek moduller
- `test_guvenlik.py` — file/path/URL safety, redact, threat detection
- `test_tools.py` — tool registry, shell, web tools
- `test_gateway.py` — platform listesi, session, mirror, pairing
- `test_acp.py` — server, client, auth
- `test_performans.py` — iteration budget, prompt cache, rate guard
- `test_model.py` — model metadata, benchmark
- `test_skills.py` — skill sayisi, kategori, arama
- `test_yardimci.py` — logging, backup, sanitization

## Dogrulama

Temizlik sonrasi:
```bash
# Core test suite
python test_suite.py

# pytest (sadece temiz dosyalar)
python -m pytest tests/ -q --tb=no
```

Her ikisi de %100 gecmelidir.
