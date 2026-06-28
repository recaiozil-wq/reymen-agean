# GÖREV: reymen_cli/main.py (14,988 satır) ve kalan büyük CLI dosyalarını böl

## NE
ReYMeN-Ajan projesindeki CLI dosyalarını alt modüllere ayır.

## HEDEF DOSYALAR

| Dosya | Satır | Hedef |
|---|---|---|
| `reymen/reymen_cli/main.py` | 14,988 | <800'er satırlık modüller |
| `reymen/sistem/cli_main.py` | 4,857 | <3000 (opsiyonel) |
| `reymen/sistem/cli_tui.py` | 3,983 | <2000 (opsiyonel) |
| `reymen/sistem/cli_commands/session_commands.py` | 3,789 | <2000 (opsiyonel) |

## ÖNCELİK

**En kritik: reymen_cli/main.py (14,988 satır)** — diğerleri opsiyonel, sıra gelirse yap.

---

## ADIM 1 (ZORUNLU): reymen_cli/main.py'yi böl

**Yer:** `reymen/reymen_cli/` — zaten 150+ dosyalık bir paket. main.py 225 fonksiyon içeriyor, hiç sınıf yok.

**Ham veri:** Hermes CLI'nin bağımsız kopyası. main.py zaten `from reymen.reymen_cli.xxx import` ile alt modülleri import ediyor (150+ dosya var). Ama 225 fonksiyon hala main.py'nin içinde duruyor.

**Yapılacak:** main.py'deki 225 fonksiyonu, konularına göre MEVCUT alt modüllere taşı veya yeni modüller oluştur.

**Mevcut modüller (örnek):** auth.py, commands.py, config.py, cron.py, gateway.py, models.py, providers.py, session.py, tools.py, plugins.py, backup.py vb.

**Bölme şeması (fonksiyon adından konu çıkar):**

| Modül | Taşınacak fonksiyonlar | Mevcut mu? |
|---|---|---|
| `gateway.py` | `gateway_*`, `_gateway_*` | ✅ var |
| `session.py` | `session_*`, `_session_*` | ✅ var |
| `commands.py` | `cmd_*`, `_cmd_*`, `handle_*` | ✅ var |
| `config.py` | `config_*`, `_config_*` | ✅ var |
| `providers.py` | `provider_*`, `_provider_*` | ✅ var |
| `models.py` | `model_*`, `_model_*` | ✅ var |
| `plugins.py` | `plugin_*`, `_plugin_*` | ✅ var |
| `cron.py` | `cron_*`, `_cron_*` | ✅ var |
| `backup.py` | `backup_*`, `_backup_*` | ✅ var |
| `setup.py` | `setup_*`, `install_*`, `_setup_*` | ✅ var |
| `display.py` | `print_*`, `show_*`, `display_*`, `format_*` | ❌ yeni |
| `termux.py` | `_termux_*` | ❌ yeni |
| `version.py` | `_read_*version*`, `_print_version*` | ❌ yeni |
| `update.py` | `update_*`, `_update_*` | ❌ yeni |

**Kural:** Her fonksiyon grubunu kendi modülüne taşı. main.py'de sadece `main()` fonksiyonu + import'lar kalsın.

**Hedef:** main.py <500 satır, her modül <800 satır.

## ADIM 2 (OPSİYONEL): Diğerlerini küçült

Zaman kalırsa:
- `cli_main.py` (4,857): TUI ile ilgili kalan kısmı `cli_tui.py`'ye taşı
- `cli_tui.py` (3,983): Alt modüllere böl (`cli_tui_statusbar.py`, `cli_tui_spinner.py`, `cli_tui_scrollback.py`)
- `session_commands.py` (3,789): Alt gruplara böl (`session_crud.py`, `session_list.py`, `session_export.py`)

## DOĞRULAMA

Her adımdan sonra:
```bash
python -c "compile(open('DOSYA.py').read(), 'DOSYA.py', 'exec'); print('OK')"
```

Tüm adımlar bitince:
```bash
python -c "from reymen.reymen_cli.main import main; print('main OK')"
python -m pytest tests/ -x --timeout=10 -q 2>&1 | tail -5
```

## YASAKLAR
- `from reymen.reymen_cli.main import main` çalışmalı (public API kırma)
- Mevcut testleri düzenleme
- __pycache__/.git/node_modules içinde değişiklik yok
- Fonksiyon mantığını değiştirme, sadece taşı
