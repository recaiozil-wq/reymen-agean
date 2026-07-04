# ReYMeN Projesi Veri Dosyası Kullanım Analizi

Tarih: 2026-07-04
Kaynak kod: `src/reymen/` ve `src/core/` altındaki .py dosyaları
Analiz yöntemi: grep ile string referans taraması

---

## 📊 VERİ DOSYASI → KOD REFERANS TABLOSU

| # | Dosya Yolu | Ref Sayısı | Okuyan Kodlar | Yazan Kodlar | Kullanım Durumu |
|---|---|---|---|---|---|
| **MERKEZ DB (kök/merkez_db)** | | | | | |
| 1 | `merkez_db/session.db` | 20 | session_db.py, session_search_tool.py, conversation_loop.py, auto_budama.py, hafiza_genislet.py, web_ui/__init__.py, _check_remaining_dbs.py | session_db.py (AdvancedSessionStorage), hafiza_genislet.py, schema_manager.py | **Çok Kullanılan** 🔴 |
| 2 | `merkez_db/ogrenme.db` | 23 | once_hafiza.py, scan_skills_to_hafiza.py / v2 / v3, scan_skills_apply.py, cron_scan_skills.py, scan_skills_to_hafiza_cron.py | cron_scan_skills.py, scan_skills_apply.py, scan_skills_to_hafiza.py/v2/v3 | **Çok Kullanılan** 🔴 |
| 3 | `merkez_db/skills_index.db` | 50+ | scan_skills_to_hafiza.py/cron/run/v2/v3, cron_scan_skills.py, cron_skill_sync.py/register, once_hafiza.py, konusmadan_skill.py, closed_learning_loop.py, conversation_loop.py, disk_izleme.py, db_config.py, migrate_skills.py, web_ui/__init__.py | scan_skills_to_hafiza.py/cron/run, cron_scan_skills.py, cron_skill_sync.py, scan_skills_apply.py | **Çok Kullanılan** 🔴 |
| 4 | `merkez_db/hatalar.db` | 2 | once_hafiza.py, _check_remaining_dbs.py | once_hafiza.py | **Az Kullanılan** 🟡 |
| 5 | `merkez_db/reymen_state.db` | 0 | — | — | **Terk Edilmiş** ⚪ |
| **KÖK DİZİN** | | | | | |
| 6 | `findings_board.db` (kök) | 0 | — | — | **Terk Edilmiş** ⚪ |
| 7 | `durum.json` | 79 | durum.py, durum_paylas.py, ortak_komut.py, bot_supervisor.py, discord_bot.py, telegram_bot.py, ortak_komutlar.py, ortak_watchdog.py, conversation_loop.py, motor.py, durum_guncelle.py, nightly_improvement.py, self_improve.py, setup_wizard.py, db_backup.py, hermes_stubs/__init__.py | durum.py, durum_paylas.py, ortak_komut.py, bot_supervisor.py, discord_bot.py, telegram_bot.py, durum_guncelle.py, nightly_improvement.py, ortak_watchdog.py | **Çok Kullanılan** 🔴 |
| **src/reymen/merkez_db/** | | | | | |
| 8 | `src/reymen/merkez_db/analitik.db` | 6 | analitik.py, db_config.py, ortak_komut.py | analitik.py, ortak_komut.py | **Az Kullanılan** 🟡 |
| 9 | `src/reymen/merkez_db/self_improve.db` | 7 | self_improve.py, curator.py, db_config.py, schema_manager.py | self_improve.py, curator.py | **Az Kullanılan** 🟡 |
| 10 | `src/reymen/merkez_db/cozum_hafizasi.db` | 1 | cozum_hafizasi.py | cozum_hafizasi.py | **Az Kullanılan** 🟡 |
| 11 | `src/reymen/merkez_db/ogrenmeler.db` | 18 | once_hafiza.py, scan_skills_to_hafiza_cron.py/run, _dogrulama.py, _hata_senaryo.py, _video_agent.py, db_config.py, schema_manager.py, _ajan_iletisim.py, _web_tetikleyici.py, web_ui/__init__.py | once_hafiza.py, scan_skills_to_hafiza_cron.py/run | **Çok Kullanılan** 🔴 |
| 12 | `src/reymen/merkez_db/hata_toplama.db` | 5 | hata_toplama.py, schema_manager.py, web_ui/__init__.py | hata_toplama.py | **Az Kullanılan** 🟡 |
| **src/reymen/hafiza/** | | | | | |
| 13 | `src/reymen/hafiza/session_search.db` | 1 | cereyan/session_search.py | cereyan/session_search.py | **Az Kullanılan** 🟡 |
| 14 | `src/reymen/hafiza/merkez_db/hafiza.db` | 12 | auto_budama.py, gorev_hafiza.py, hafiza_budama.py, hafiza_genislet.py, session_search_tool.py, hermes_to_reymen.py, db_config.py | hafiza_genislet.py, hermes_to_reymen.py | **Az Kullanılan** 🟡 |
| **src/reymen/sistem/** | | | | | |
| 15 | `src/reymen/sistem/findings_board.db` | 0 | — (findings_board.py shared_state/findings_board.db kullanıyor) | — | **Terk Edilmiş** ⚪ |
| **shared_state/** | | | | | |
| 16 | `shared_state/findings_board.db` | 4 | findings_board.py, health_check.py | findings_board.py | **Az Kullanılan** 🟡 |
| 17 | `shared_state/git_watchdog_state.json` | 3 | git_watchdog.py | git_watchdog.py | **Az Kullanılan** 🟡 |
| 18 | `shared_state/reymen_state.json` | 1 | db_backup.py | db_backup.py | **Terk Edilmiş** ⚪ |
| **src/shared_state/** | | | | | |
| 19 | `src/shared_state/findings_board.db` | 0 | — | — | **Terk Edilmiş** ⚪ |
| **skills/** | | | | | |
| 20 | `skills/improvements.db` | 4 | nightly_improvement.py, skill_iyilestirici.py, findings_board.py | nightly_improvement.py, skill_iyilestirici.py | **Az Kullanılan** 🟡 |
| **.ReYMeN/** | | | | | |
| 21 | `.ReYMeN/session.db` | 15+ | conversation_loop.py, auto_budama.py, session_search_tool.py, guncelle.py, _check_remaining_dbs.py, schema_manager.py, web_ui/__init__.py | auto_budama.py, schema_manager.py | **Çok Kullanılan** 🔴 |
| 22 | `.ReYMeN/analitik.db` | 0 | — (merkez_db/analitik.db kullanılıyor) | — | **Terk Edilmiş** ⚪ |
| 23 | `.ReYMeN/auth/auth.db` | 1 | reymen_auth.py | reymen_auth.py | **Az Kullanılan** 🟡 |
| 24 | `.ReYMeN/oauth/oauth_tokens.db` | 9 | oauth_sistemi.py | oauth_sistemi.py | **Az Kullanılan** 🟡 |
| 25 | `.ReYMeN/sohbet_bot_arkiv/state.db` | 0 | — | — | **Terk Edilmiş** ⚪ |
| 26 | `.ReYMeN/backup_state.json` | 1 | db_backup.py | db_backup.py | **Az Kullanılan** 🟡 |
| 27 | `.ReYMeN/skill_registry.json` | 2 | skill_activator.py, skill_aktive_et.py | skill_aktive_et.py | **Az Kullanılan** 🟡 |
| 28 | `.ReYMeN/cron/jobs.json` | 12+ | cron_skill_sync.py/register, jobs.py, guncelle.py, web_ui/__init__.py | cron_skill_sync.py | **Az Kullanılan** 🟡 |
| 29 | `.ReYMeN/watchdog_hash.json` | 1 | ortak_watchdog.py | ortak_watchdog.py | **Az Kullanılan** 🟡 |
| 30 | `.ReYMeN/web/users.json` | 4 | web_ui/auth.py, web_ui/__init__.py | web_ui/auth.py | **Az Kullanılan** 🟡 |
| 31 | `.ReYMeN/a2a_nodes.json` | 3 | a2a_distributed.py | a2a_distributed.py | **Az Kullanılan** 🟡 |
| 32 | `.ReYMeN/stats/tools_used.json` | 1 | motor.py | motor.py | **Az Kullanılan** 🟡 |
| 33 | `.ReYMeN/update_check.json` | 1 | self_update.py | self_update.py | **Az Kullanılan** 🟡 |
| **KODDA TANIMLI AMA FİZİKSEL DOSYASI KONTROL EDİLMEDİ** | | | | | |
| 34 | `.ReYMeN/continuous_learning.db` | 16 | continuous_learning.py, conversation_loop.py, db_config.py, web_ui/__init__.py | continuous_learning.py | **Aktif (çok kullanılan)** 🔴 |
| 35 | `.ReYMeN/nudge_model.db` | 2 | nudge_model.py | nudge_model.py | **Az Kullanılan** 🟡 |
| 36 | `.ReYMeN/skill_library.db` | 12 | skill_library.py, skill_activator.py, fix_skills_path.py, motor.py, web_ui/__init__.py | skill_library.py, skill_activator.py | **Aktif (orta)** 🟡 |
| 37 | `.ReYMeN/kanban.db` | 4 | kanban_orchestrator.py, ReYMeN_state.py, _check_remaining_dbs.py | kanban_orchestrator.py | **Az Kullanılan** 🟡 |
| 38 | `.ReYMeN/state.db` | 66+ | ReYMeN_state.py, session_db.py, cli_session.py, cli_commands.py, handoff_handler.py, cli_main.py, cli_mixin_core.py, web_ui/__init__.py, run_agent.py, proaktif_bakim.py, kiral38_watchdog.py, hermes_to_reymen.py, gateway/session.py, gateway/slash_commands.py | ReYMeN_state.py, session_db.py, proaktif_bakim.py, cli_main.py, cli_mixin_core.py | **Çok Kullanılan** 🔴 |
| 39 | `.ReYMeN/skills_index.db` | 50+ | (skills_index.db ile aynı grup) | — | **skills_index.db altında** |
| 40 | `merkez_db/memory.db` | 6 | ogrenme.py, vector_memory.py, memory_provider.py | ogrenme.py, vector_memory.py | **Az Kullanılan** 🟡 |
| 41 | `steering.db` | 0 | — | — | **Hiç tanımlanmamış** ⚪ |
| 42 | `.ReYMeN/proaktif_ogrenme.db` | 1 | proaktif_kontrol.py | proaktif_kontrol.py | **Az Kullanılan** 🟡 |

---

## 🔍 ÖNE ÇIKAN BULGULAR

### 🟢 Sağlıklı (düzenli okuma+yazma, aktif kullanım)
| Dosya | Açıklama |
|---|---|
| `durum.json` | Sistemin nabzı — 30+ Python dosyası tarafından okunup yazılıyor |
| `merkez_db/session.db` / `.ReYMeN/session.db` | Ana konuşma veritabanı, sürekli okuma/yazma |
| `merkez_db/skills_index.db` | Beceri indeksi — çok sayıda cron/scan dosyası tarafından aktif kullanılıyor |
| `merkez_db/ogrenme.db` | Öğrenme DB'si, regex taramalı cron'lar tarafından güncelleniyor |
| `src/reymen/merkez_db/ogrenmeler.db` | OnceHafiza öğrenme veritabanı |
| `.ReYMeN/state.db` | Ana state DB, neredeyse tüm CLI/session bileşenleri kullanıyor |

### 🟡 Az Kullanılan / Tek Noktaya Bağımlı
| Dosya | Risk |
|---|---|
| `src/reymen/merkez_db/cozum_hafizasi.db` | Sadece 1 Python dosyası |
| `src/reymen/hafiza/session_search.db` | Sadece 1 Python dosyası |
| `skills/improvements.db` | Sadece nightly scriptleri |
| `.ReYMeN/auth/auth.db` | Sadece reymen_auth.py |
| `.ReYMeN/watchdog_hash.json` | Sadece ortak_watchdog.py |

### ⚪ Terk Edilmiş (fiziksel dosya var ama kod referansı yok veya ölü kod)
| Dosya | Durum |
|---|---|
| `merkez_db/reymen_state.db` | Kodda hiç referans yok |
| `findings_board.db` (kök) | Kodda hiç referans yok |
| `src/reymen/sistem/findings_board.db` | Kod shared_state/findings_board.db kullanıyor, bu artık kullanılmıyor |
| `src/shared_state/findings_board.db` | Kodda hiç referans yok |
| `.ReYMeN/analitik.db` | src/reymen/merkez_db/analitik.db varken bu kopya ölü |
| `.ReYMeN/sohbet_bot_arkiv/state.db` | Kodda hiç referans yok |
| `shared_state/reymen_state.json` | Sadece db_backup.py'da yedekleme listesinde |

### 🚨 Veri Dağınıklığı (çoklu kopyalar)
| Veri Kümesi | Kopyalar |
|---|---|
| `findings_board.db` | **4 kopya**: kök/, src/reymen/sistem/, shared_state/, src/shared_state/ |
| `analitik.db` | **2 kopya**: src/reymen/merkez_db/, .ReYMeN/ |
| `session.db` | **2 kopya**: merkez_db/, .ReYMeN/ |
| `skills_index.db` | **2 kopya**: merkez_db/, .ReYMeN/ (farklı yollar referans ediliyor) |

### 📋 İSTATİSTİK ÖZETİ
- Toplam veri dosyası (fiziksel): ~25
- Çok kullanılan (🔴): 7
- Az kullanılan (🟡): 18
- Terk edilmiş (⚪): 6
- Kodda tanımlı ama fiziksel durumu bilinmeyen: 5
- **Hiç referansı olmayan (steering.db)**: 1
