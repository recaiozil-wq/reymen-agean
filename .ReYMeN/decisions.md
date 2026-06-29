## Karar #36: TUI Hermes Seviyesine Yükseltme

**Ne yapıldı:** `tui.py` sade metin → prompt_toolkit + Rich tabanlı etkileşimli TUI

**Neden:** Mevcut tui.py (314 satır) sadece statik renkli çıktı fonksiyonlarıydı. Gerçek bir Terminal UI (komut girişi, geçmiş, otomatik tamamlama, panel sistemi) yoktu.

**Alternatifler:**
1. Sadece Rich fonksiyonları bırakmak → etkileşimsiz
2. Ayrı cli_tui.py modülü → dağınıklık
3. Mevcut tui.py'yi komple yeniden yazmak → Seçilen yol

**Eklenenler:**
- ReYMeNTUI class: prompt_toolkit tabanlı REPL (otomatik tamamlama, geçmiş, klavye kısayolları)
- Rich çıktı fonksiyonları korundu (info, success, warning, error, panel, table)
- Motor tool'u: TUI_BASLAT
- Fallback: prompt_toolkit yoksa basit input() REPL
## Karar #31 — Bot Çince cevap fix + Ensemble akışı

**Ne yapıldı?**
1. Hermes reymen profili SOUL.md'sine Türkçe talimatı eklendi (başa)
2. telegram_bot/__init__.py AIAgentOrchestrator → ConversationLoop ensemble akışına çevrildi
3. conversation_loop.py'ye .env yükleme eklendi (API key okunamıyordu)
4. OnceHafiza'daki eski Çince kayıt (dunyada guncel haberler) temizlendi
5. Gateway restart yapıldı

**Neden?**
- SOUL.md'de Türkçe talimatı yoktu → DeepSeek Çince cevap veriyordu
- Bot main.py'deki ağır ReAct döngüsü yerine ensemble akışı kullanmalı (DeepSeek önce toolsuz cevaplasın, sonra puanla karşılaştır)
- conversation_loop.py'de load_dotenv yoktu → API key bulunamıyordu

**Alternatif?**
- conversation_loop.py'deki ensemble zaten yazılıydı, sadece bot yönlendirilmedi
- SOUL.md'yi proje köküne koymak da çözümdü ama profil override ediyor

## Karar #42 — Auth: Hermes Pattern JWT + Role Bazli

**Ne yapildi:** Mevcut auth.py + web_ui/__init__.py auth sistemi Hermes dashboard_auth pattern'ine donusturuldu.

**Neden:** Kullanici "Jwt var role bazli hermes de olan sekili ile yap" dedi — Hermes'teki AuthProvider ABC + Session dataclass + provider registry + cookie yonetimi birebir uygulandi.

**Detay:**
- AuthProvider ABC (Hermes DashboardAuthProvider pattern)
- Session dataclass (user_id, display_name, role, provider, expires_at, access_token, refresh_token)
- Provider registry: register_provider(), get_provider(), list_providers()
- PasswordAuthProvider: complete_password_login(), verify_session(), refresh_session(), revoke_session()
- Cookie: hermes_session_at (access token) + hermes_session_rt (refresh token)
- Transparent refresh: access token expiredsa refresh token ile otomatik rotate
- /api/auth/me — mevcut Session bilgisi
- /api/auth/providers — kayitli provider listesi
- Audit logging (AuditEvent.LOGIN_SUCCESS/FAILURE/LOGOUT)
- Role bazli izin (admin/operator/viewer) middleware'de
- Eski _get_user/_require_auth/_izin_kontrol helper'lari temizlendi
- Commit: 61846927

**Karar:** Kabul. Hermes'teki ile birebir ayni desen.

## Karar #43 — CLI Handler Ayristirma (83 _handle_ komutu ayrı dosyalara)

**Ne yapıldı:** reymen/sistem/cli_commands/ altındaki 83 adet `_handle_*` komutu ayrı dosyalara bölündü.

**Neden:** Kullanıcı "Kalan 73 handler diğer cli modül de yap" dedi — config_commands.py (585 satır), edit_commands.py, session_commands.py, system_commands.py, tool_commands.py icindeki handler'lar handlers/ altındaki kendi dosyalarına tasindi.

**Detay:**
- handlers/config/ (8): profile, gquota, personality, skin, footer, reasoning, busy, fast
- handlers/edit/ (7): rollback, snapshot, stop, agents, paste, copy, image
- handlers/session/ (5): handoff, resume, sessions, branch, approval
- handlers/system/ (5): goal, subgoal, debug, update, voice
- handlers/tools/ (9): tools, codex_runtime, cron, curator, kanban, skills, background, bundles, browser
- Toplam: 34 standalone handler + 6 __init__.py = 40 dosya
- config_commands.py: model_picker_selection, model_switch class state'e bağlı, ayrılmadi (10. ve 11. handler olarak kaldi)
- cli_commands/ haricinde hicbir dosya degistirilmedi
- Tüm syntax OK
- Commit: 7267f552

## Karar #44 — .reyplugin CLI + Schema Konsolidasyon

**Ne yapıldı:**
- .reyplugin export/import CLI komutlari calisir hale getirildi (_cmd_plugin())
- Twin module drift fix: sistem/schema_manager -> core/schema_manager import wrapper
- VERITABANLARI (5 DB) + motor_kaydet() + durum_text()
- Alembic migration HEAD uygulandi (session.db)

**Neden:** Kullanici backlog'da .reyplugin ❌ ve Alembic ⏸️ olarak isaretlemisti.
- .reyplugin: Python API calisiyordu ama CLI komutu yoktu
- Alembic: ikiz modul sorunu + migration uygulanmamisti

**Karar:** Kabul. Commit 700269d7.

## Karar #45 — Kısmen Var (7) Tamam

**Ne yapildi:** 7 kismen var ozelligin eksik kisimlari dolduruldu.

**Neden:** Kullanici backlog'da 7 ozelligi "kismen var" olarak isaretlemisti.

**Yapilanlar:**
1. MCP: auto-discovery (config+.env) + reconnect heartbeat (375s)
2. Plugin: hot-reload (importlib) + provider plugin kavrami
3. Skills: SQLite kutuphane (290s) + otomatik aktivasyon (sorgudan_aktif_et, 220s)
4. Web Search: multi-backend ABC (DDG/Google/Bing) - 381s
5. Image Gen: multi-backend ABC (FAL/OpenAI/xAI/Stub) - 437s
6. Browser: multi-backend ABC (Playwright MCP/Browser Use) - 562s
7. Security: network restriction (938s) + Docker sandbox entegrasyonu

**Commit:** (son commit)
