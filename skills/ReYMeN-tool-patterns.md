---
name: ReYMeN-tool-patterns
category: software-development
version: 1.0.0
description: ReYMeN projesinde tool gelistirme pattern'leri ve kritik kod yapilari
tags: [skill, hermes, ReYMeN, patterns, tools]
---

# ReYMeN-tool-patterns

ReYMeN projesine yeni tool eklerken kullanilacak pattern'ler.

## Ozet Tablo

| # | Dosya | Kritik Pattern |
|---|-------|----------------|
| 1 | session_search_tool.py | Lazy store + _parse_limit + dict/tuple kayit guard |
| 2 | execute_code_tool.py | Lazy lab + TimeoutError/MemoryError ayrimi |
| 3 | delegate_task_tool.py | sys.executable + returncode kontrolu + json_cikti flag |
| 4 | vision_tool.py | mkstemp + lazy PIL + ayri exception tipi |
| 5 | discord.py | Interface uyumu + mesaj_akisi generator |
| 6 | test_tools.py | monkeypatch + network mock + her tool icin 3-4 case |
| 7 | context_tool.py | Lazy ctx + method adi fallback chain + TypeError retry |
| 8 | memory_providers/base.py | ABC BellekSaglayici interface — kaydet/oku/ara/sil/durum |
| 9 | memory_providers/file_provider.py | Atomic write (temp+rename) + JSON bozuk dosya recovery |
| 10 | memory_providers/chromadb_provider.py | upsert duplicate-safe + n_results ≤ count() guard |
| 11 | memory_providers/sqlite_provider.py | FTS5 check via compileoption + executescript DDL + LIKE fallback |
| 12 | memory_providers/redis_provider.py | scan_iter lazy iterator + namespace index (sadd) + decode_responses |
| 14 | powerbi_mcp_tool.py | MCP subprocess + JSON-RPC 2.0 + VBileşen kontrolu (tasklist) |
| 15 | video_analysis_tool.py | youtube-transcript-api fallback → yt-dlp + VTT→metin donusumu |
| 16 | n8n_tool.py | REST API + Bridge API (localhost:15680) + requests Session |
| 17 | swarm_tool.py | ThreadPoolExecutor + SwarmTask/SwarmResult dataclass + as_completed |

## Klas Tabanli Tool Sablonu (v2 - Genisletilmis)

2026-06-26'da 4 tool (powerbi_mcp, video_analysis, n8n, swarm) icin kullanilan pattern:

```python
# -*- coding: utf-8 -*-
\"\"\"tool_adi.py — Aciklama.\"\"\"

import json
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class ToolSinifHatasi(Exception):
    \"\"\"Tool islem hatasi.\"\"\"


class ToolSinifi:
    \"\"\"Tool sinifi.

    Ornek:
        tool = ToolSinifi()
        tool.islem_yap(parametre)
    \"\"\"

    def __init__(self, parametre: Optional[str] = None):
        self._parametre = parametre

    def islem_yap(self, girdi: str) -> dict:
        try:
            # islem mantigi
            return {"success": True, "result": girdi}
        except Exception as e:
            logger.error("Islem hatasi: %s", e)
            return {"success": False, "error": str(e)}


# CLI GIRIS NOKTASI
def run(islem: str = \"default\", ...) -> str:
    \"\"\"Tool CLI giris noktasi.

    Args:
        islem: alt islem adi
        ...: diger parametreler

    Returns:
        str: JSON formatinda sonuc
    """
    tool = ToolSinifi()
    if islem == \"default\":
        sonuc = tool.islem_yap(...)
    else:
        sonuc = {\"success\": False, \"error\": f\"Bilinmeyen islem: {islem}\"}
    return json.dumps(sonuc, ensure_ascii=False, indent=2)


if __name__ == \"__main__\":
    import sys
    print(run(*sys.argv[1:]))
```

### Klas vs Fonksiyonel Pattern Karsilastirmasi

| Boyut | Fonksiyonel (eski) | Klas Tabanli (yeni) |
|:------|:-------------------|:--------------------|
| State | Yok (global degisken) | self.* ile saklanir |
| Birden cok instance | Mumkun degil | Her cagrida yeni ornek |
| Test edilebilirlik | Zor (global state) | Kolay (mock injection) |
| Ozel exception | Yok | ToolSinifHatasi |
| Property | Yok | @property ile durum sorgulama |
| Karma metodlar | Mumkun degil | _private + public metodlar |
| JSON cikti | Manuel | json.dumps(ensure_ascii=False) |

### 4 Yeni Tool'un Ozellikleri

| Tool | Sinif | Kritik Pattern |
|:-----|:------|:---------------|
| powerbi_mcp_tool.py | `PowerBIMCPTool` | `_mcp_yolunu_bul()` — filesystem tarama + fallback; `_powerbi_kontrol()` — tasklist ile PID dogrulama |
| video_analysis_tool.py | `VideoAnalysisTool` | 2-seviye fallback (youtube_transcript_api → yt-dlp); `_vtt_to_text()` — VTT temizleme; `_extract_video_id()` — regex ile ID |
| n8n_tool.py | `N8NTool` | requests.Session + Bridge API (localhost:15680); `health_check()` → `trigger_workflow()` on kosul |
| swarm_tool.py | `SwarmTool` | `ThreadPoolExecutor` + `SwarmTask/SwarmResult` dataclass; `run_parallel/sequential/pipeline` 3 mod |

## Standart Tool Sablonu (Eski)

```python
# -*- coding: utf-8 -*-
"""ornek_tool.py — Aciklama."""

from __future__ import annotations
from typing import Any

_VAR: Any = None  # Lazy

def _get_var():
    global _VAR
    if _VAR is None:
        from module import Class  # gec import
        _VAR = Class()
    return _VAR

def run(param: str = "") -> str:
    if not param:
        return "[Hata]: param parametresi gerekli."
    try:
        obj = _get_var()
        return str(obj.islem(param))
    except Exception as e:
        return f"[Hata]: {e}"

def motor_kaydet(motor) -> None:
    motor._plugin_arac_kaydet("ORNEK", run, "Aciklama")
```

## Motor'a Kayit

Her yeni tool `motor.py`'de `_plugin_moduller_yukle()` listesine eklenir:

```python
"tools.ornek_tool",
```

## Hermes Eksiklik Kapatma — Toplu Modul Sablonu

Hermes Agent'da olup ReYMeN'de olmayan ozellikleri kapatmak icin toplu modul yazimi:

### Kullanici Duzeltmesi (KRITIK)
Kullanici "18 eksiklik var, hepsini yaz" dediginde TEK TEK degil, HEPSINI birden yaz.
Ilk seferde 1 tane yazdim → "tek tek kapsamlı mi?" diye uyardi. **Batch modu**: tum eksikleri tek seferde kapat.

### 13 Yeni Modul (2026-06-25) — Hermes Eksiklik Kapatma
| Modul | Hermes Karsiligi | run() Parametreleri |
|-------|-----------------|---------------------|
| `web_extract_tool.py` | web_extract | `urls, timeout` |
| `vision_analyze_tool.py` | vision_analyze | `image_url, question, ocr, dil` |
| `image_generate_tool.py` | image_generate | `prompt, aspect_ratio, negative_prompt, provider` |
| `todo_tool.py` | todo | `islem, icerik, gorev_id, durum, oncelik, etiketler` |
| `process_tool.py` | process | `islem, pid, komut, calisma_dizini, timeout, son_satir` |
| `file_ops_tool.py` | patch/write_file/search_files | `islem, path, content, old_string, new_string, pattern, target, file_glob, offset, limit, context, replace_all` |
| `cron_tool.py` | cronjob | `islem, job_id, ad, zamanlama, komut, aciklama` |
| `memory_batch_tool.py` | memory (batch) | `islem, target, content, old_text, new_text, operations, ne_yaptin, neden, alternatif` |
| `profile_tool.py` | profile system | `islem, profil_ad, aciklama, model, provider, renk` |
| `approval_tool.py` | approval policy | `islem, tool, args, kategori, pattern, reason` |
| `multi_platform_tool.py` | multi-platform | `islem, platform, chat_id, mesaj, platformlar, ad, tip, webhook_url` |
| `browser_mcp_tool.py` | Playwright MCP | `islem, url, target, text, key, js_code, direction, amount, full_page, double_click, submit, slowly, level, filter_url, index, accept` |
| `powershell_tool.py` | terminal (PS/CMD/Bash) | `komut, shell, calisma_dizini, timeout, yonetici` |

### Telegram Mesaj Formatlama
ReYMeN Telegram botunda `_formatla_metin()` fonksiyonu kullanilir.
Numaralı listeler (1. 2. 3.) satır icinde kaldiginda otomatik olarak satır basına tasinir.

Pattern: `reymen/ag/telegram_bot.py` → `_formatla_metin()` fonksiyonu `gonder()` icinde cagrilir.
Regex: `r'(?<!\d)(\d{1,3}\.\s)'` ile satır icindeki numaraları split et, her numarayı yeni satıra koy.

**Kullanıcı tercihi:** Kullanıcı "görevdeki aritmetik sayılar satır başından başlamalı" dedi.
Bu, ReYMeN'in TUM mesaj gonderme akisinda uygulanmali — sadece telegram_bot.py degil,
gateway platform mesajlarinda da ayni formatlama yapılmalı.

### Motor Entegrasyonu
`reymen/cereyan/motor.py` → `_plugin_moduller_yukle()` listesine ekle:
```python
"reymen.arac.web_extract_tool",
"reymen.arac.vision_analyze_tool",
# ... (12 modul)
```

### run() Sozlesmesi (Genisletilmis)
Her tool modulu icin `run()` fonksiyonu:
1. Parametrelerin hepsi `str` tipinde (motor string gonderir)
2. `islem` parametresi ile alt islem secilir (ornek: `islem="ekle"`, `islem="listele"`)
3. Hata durumunda `"[Hata]: ..."`, basari durumunda `"✅ ..."` dondur
4. Singleton pattern: `_mgr = None` + `_get_mgr()` lazy init
5. Motor'a kayit: `_plugin_moduller_yukle()` listesinde `"reymen.arac.MODUL_ADI"` formati

## Altyapi Sertleştirme Modülleri (2026-06-25)

Hermes Agent derinlemesine analiz sonucu 23 eksiklik tespit edildi (8 kritik, 8 orta, 7 düşük).
5 yeni altyapi modülü + 16 modülde print→log çevirisi yapıldı.

| Modul | Konum | Islev |
|-------|-------|-------|
| `reymen_logging.py` | `reymen/sistem/` | Merkezi logging, RotatingFileHandler, REYMEN_LOG_LEVEL env |
| `security_hardened.py` | `reymen/guvenlik/` | Fail-closed, komut kara liste, yol traversalkoruma, XSS/SQL injection |
| `config_manager.py` | `reymen/sistem/` | Tek config.json, env override, varsayılan değerler, derin birleştirme |
| `lazy_loader.py` | `reymen/sistem/` | LazyModule/LazyTool/ModuleRegistry, startup 100-500ms→5-10ms |
| `health_check.py` | `reymen/sistem/` | Modül/araç/bağımlılık/hafıza/config kontrolü, sağlık raporu |

### print→log Migration Pattern
Motor.py ve 16 kritik modülde `print()` → `log.info()/warning()/error()` çevirisi:
```python
# ÖNCE
print(f"[Motor] {hata_sayisi} modul yukleme hatasi:")
# SONRA
log.warning(f"{hata_sayisi} modul yukleme hatasi:")
```
Regex batch çevirisi: `reymen/sistem/test_reymen_hermes_duzeltmeler.py` → execute_code ile otomatik.
Kural: `print(f"[TAG] ...")` → `log.info(f"...")`, `print(f"[Hata] ...")` → `log.error(f"...")`

### Fail-Closed Güvenlik Pattern
Güvenlik modülü yüklenemezse araç devre dışı kalır (lambda bypass YASAK):
```python
# YANLIŞ (eski)
try:
    from file_safety import guvenli_mi as _dosya_guvenli
except ImportError:
    _dosya_guvenli = lambda p: (True, "")  # ← GÜVENLİK AÇIĞI

# DOĞRU (yeni)
try:
    from reymen.guvenlik.security_hardened import get_guard
    _guard = get_guard()
except Exception:
    _guard = None  # Araç devre dışı
```

### Motor.py God Object Tespiti
Motor.py 1664 satır, 77KB — god object anti-pattern.
Çözüm: Ayrı sınıflara parçalanacak (ToolExecutor, ToolRegistry, ToolGuardrails, TelegramTool, TorTool, WatchdogTool).
Bu büyük refactor şimdilik ertelendi ama logging + print→log ile kısmi iyileştirme yapıldı.

## Pitfall'lar

| Hata | Cozum |
|------|-------|
| `liste` eylemi → `store.son_oturumlar()` bulunamadi | `dir(store)` ile gercek method adlarini kontrol et, uymuyorsa fallback mesaj goster |
| SQLite DDL → `incomplete input` | Trigger'lar noktali virgul icerdigi icin `split(";")` bozar. **`executescript()`** ile tek seferde gonder |
| FTS5 kontrolu → `SELECT fts5(?)` hata veriyor | `SELECT sqlite_compileoption_get(0)` ile "FTS5" string'i ara |
| `context_tool.py` → `compress()` missing 1 argument | `AdvancedContextCompressor.compress(mesajlar)` gerektirir — tool disindan cagrilamaz, sadece ReAct dongusu icinde calisir |
| Docker `from_env()` hatasi | `import docker` basarili ama daemon calismiyor. `ping()` ile ek kontrol ekle, fallback local subprocess'e dus |
| **Windows path docstring** → `SyntaxError: unicodeescape` | Docstring icinde `C:\Users\...` yazma — `\U` unicode escape algilanir. `C:/Users/...` (forward slash) veya raw string `r"..."` kullan |
| **PowerShell subprocess encoding** → Türkçe karakter bozulması | `text=True` KULLANMA. Bytes al + `.decode("utf-8", errors="replace")`. PowerShell prefix: `[Console]::OutputEncoding = [System.Text.Encoding]::UTF8;` |
| **playwright CLI not found** → PATH'te değil | `python -m playwright install chromium` kullan, `playwright install chromium` değil |
| **Hermes venv vs sistem Python** → Paket bulunamadı | `sys.executable` Hermes venv'ini kullanır. Sistem paketleri icin tam path gerekli |

```bash
python -m py_compile tools/ornek_tool.py
python -m pytest tests/ -v
```
