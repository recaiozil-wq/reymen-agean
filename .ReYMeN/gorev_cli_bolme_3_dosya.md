# GÖREV: 3 Büyük CLI Dosyasını Böl

## NE
ReYMeN-Ajan projesindeki 3 büyük .py dosyasını alt modüllere ayır:

1. `reymen/sistem/cli_main.py` — 12,803 satır (294 metot, 1 sınıf)
2. `reymen/sistem/cli_mixin_commands.py` — 8,693 satır (180 metot, 1 sınıf)
3. `reymen/reymen_cli/main.py` — 14,988 satır (225 fonksiyon)

## NİYE
800+ satırlık dosyalar bakımı zorlaştırıyor, import döngülerine yol açıyor, Cline/Claude Code token limitini şişiriyor. Hermes'te de aynı standart uygulanıyor (cli.py 15,762 → 485'e düştü).

## NASIL

### ADIM 1: cli_mixin_commands.py (8,693 → <500'er satırlık modüller)

**Yer:** `reymen/sistem/cli_commands/` (paket)
**Ham veri:** 180 metot, MixinCommands sınıfı
**Bölme şeması (fonksiyon adına göre grupla):**

| Modül | İçerik |
|---|---|
| `__init__.py` | MixinCommands stub, alt modülleri import eder |
| `base.py` | Ortak yardımcılar: `_slow_command_status`, `_command_spinner_frame`, `_busy_command`, `_open_external_editor`, `show_banner`, `_display_resumed_history` |
| `edit_commands.py` | Düzenleme: `_handle_copy_command`, `_handle_paste_command`, `_handle_rollback_command`, `_handle_snapshot_command`, `_handle_stop_command`, `_handle_agents_command`, `_recover_terminal_input_modes`, `_write_osc52_clipboard` |
| `file_commands.py` | Dosya: `_handle_edit_command`, `_handle_read_command`, `_handle_write_command`, `_handle_patch_command`, `_handle_ls_command` vb. dosya işlemleri |
| `tool_commands.py` | Tool: `_handle_run_command`, `_handle_execute_command`, `_handle_web_command`, `_handle_search_command` vb. tool çağrıları |
| `session_commands.py` | Oturum: `_handle_session_command`, `_handle_history_command`, `_handle_new_command`, `_handle_reset_command` |
| `config_commands.py` | Konfigürasyon: `_handle_config_command`, `_handle_profile_command`, `_handle_env_command` |
| `system_commands.py` | Sistem: `_handle_help_command`, `_handle_version_command`, `_handle_status_command`, `_handle_update_command` |

**Kural:** Her metot grubunu ilgili .py'ye taşı. MixinCommands sınıfı `__init__.py`'de tanımlı kalır, her alt modül `@property` veya fonksiyon olarak eklenir. VEYA alt modüller doğrudan fonksiyon olarak tanımlanır, MixinCommands bunları import eder.

**Alternatif (daha basit):** MixinCommands'ı tamamen fonksiyon tabanlı yap. Her alt modül bir fonksiyon grubu döndürür. MixinCommands.__init__()'de bunları self._command_registry'e yükler.

**Hedef:** Her modül <800 satır.

### ADIM 2: cli_main.py (12,803 → 2-3 parça)

**Yer:** `reymen/sistem/cli_main.py` — mevcut dosyayı koru, içinden ağır blokları çıkar

**Ham veri:** ReYMeNCLI sınıfı, 294 metot. Mixin'ler (cli_mixin_*) zaten import ediliyor.
**Bölünecek bölümler:**

| Çıkarılacak | Yeni dosya |
|---|---|
| TUI/UI ile ilgili metotlar (~2000 satır): `_status_bar_*`, `_build_context_bar`, `_format_prompt_elapsed`, `_tui_*`, `_spinner_*`, `_scrollback_*` | `cli_tui.py` |
| Agent/startup ile ilgili metotlar (~1500 satır): `_prepare_deferred_agent_startup`, `_run_cleanup`, agent lifecycle | `cli_agent.py` |
| Geri kalan | `cli_main.py`'de kalır |

**Hedef:** cli_main.py <5000 satır.

### ADIM 3: reymen_cli/main.py (14,988 → <500'er satırlık modüller)

**Yer:** `reymen/reymen_cli/main.py` — mevcut dosyayı koru

**Ham veri:** 225 fonksiyon, hiç sınıf yok. Hermes CLI'nin bağımsızlaştırılmış kopyası.
**Bölme şeması (fonksiyon adına göre):**

| Modül | İçerik |
|---|---|
| `main.py` | Sadece `main()` ve argüman ayrıştırma, geri kalanı import |
| `termux.py` | `_is_termux_*`, `_termux_bundled_*` — Termux başlangıç kodları |
| `version.py` | `_read_openai_version_*`, `_print_fast_version_info`, `_read_git_revision_*` |
| `setup.py` | Kurulum/yapılandırma fonksiyonları |
| `gateway_cmds.py` | Gateway ile ilgili komutlar |
| `provider_cmds.py` | Provider/model yönetimi |
| `session_cmds.py` | Oturum yönetimi |
| `tool_cmds.py` | Tool çağrıları |
| `display.py` | Çıktı/ekran formatlama |

**Hedef:** Her modül <800 satır, main.py <500 satır.

## DOĞRULAMA

Her adımdan sonra:
```
python -c "compile(open('DOSYA.py').read(), 'DOSYA.py', 'exec'); print('OK')"
```
Tüm adımlar bitince:
```
python -m pytest tests/ -x --timeout=10 -q 2>&1 | tail -5
```

## YASAKLAR
- Mevcut çalışan herhangi bir modülün public API'sini değiştirme
- `from reymen.sistem.cli_main import ReYMeNCLI` çalışmalı (import kırma)
- `reymen/reymen_cli/main.py`'nin `main()` fonksiyonu aynı kalmalı
- __pycache__/.git/node_modules/bot_venv içinde değişiklik yok
- Test dosyalarını düzenleme (şimdilik)
