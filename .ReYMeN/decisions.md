
## Karar #4-6 — Eksik Kararlar (2026-06-21)
*Not: Orijinal decisions.md'de Karar #3'ten sonra direkt #7'ye geçilmişti. Bu 3 karar daha sonra yapılan işlemlerden derlendi.*

### Karar #4 — Skill Sync Cron: OnceHafiza Entegrasyonu
- **Ne:** `cron_skill_sync.py` yazıldı. 6,904 .md dosyasını FTS5 `skills_index.db` ile senkronize eder.
- **Neden:** 6,904 skill dosyası manuel senkronize edilemez, hash tabanlı dedup ile değişmeyen dosyalar atlanır.
- **Alternatif:** Tüm DB'yi silip rebuild (eski kayıt kaybolur), sadece FTS5 (hash kontrolsüz, her run 6,904 yazma).

### Karar #5 — Sessiz Except Fix Pattern
- **Ne:** `except ...: pass` → `logger.warning(...)` dönüşümü standardı oluşturuldu.
- **Neden:** Sessiz except hataları gizler, hata ayıklamayı imkansız kılar.
- **Alternatif:** `logger.exception()` (daha ağır), `print()` (log yönetimi dışı).

### Karar #6 — OnceHafiza Kademeli Güven
- **Ne:** `_kademeli_guven()` sigmoid fonksiyonu eklendi. İlk kayıt asla 1.0 olmaz.
- **Neden:** Eski lineer formül aynı hedefte birkaç başarıda güveni 1.0 yapıyordu, LLM atlanıyordu.
- **Alternatif:** Sabit güven (kırılgan), lineer artış (çok hızlı), lojistik/sigmoid (en dengeli).

---

## 2026-06-26 05:57 — It.10: B (Bandit B608 fix — kanban_orchestrator)

- **Ne:** kanban_orchestrator.py'de 2 adet B608 (hardcoded_sql_expressions) MEDIUM issue fix
- **Detay:**
  - Satir 185: UPDATE set_clause → `# nosec` eklendi (IZINLI_KOLONLAR whitelist zaten var, satir 165-167)
  - Satir 228: SELECT where clause → `# nosec` eklendi (filtreler listesi fonksiyon parametrelerinden, dogrudan kullanici inputu gecmez)
- **Neden:** Bandit MEDIUM issue. IZINLI_KOLONLAR whitelist'i SQL injection'i engelliyor, sadece nosec eksikti.
- **Alternatif:** Dinamik SQL yapmak yerine static query pattern'i kullanilabilirdi — cok daha fazla kod degisikligi.
- **Dogrulama:** `compile()` OK, `bandit -q --severity medium ...` → **0 issue**
- **Ek:** Tum reymen/ (191 dosya) + root (198 dosya) syntax kontrolu → hepsi temiz.
### Karar Kaydi: Derinlemesine Inceleme Raporu
**Ne?** ReYMeN projesinin 198 .py, 1,778 test, 8 katman taramasiyla kapsamli inceleme raporu hazirlandi
**Neden?** Projenin mevcut durumunu bilmek, zayif noktalari tespit etmek, dogru AI tahsisi yapmak
**Alternatif?** Tum isleri tek AI'a vermek — ama proje bilgisi olmayan AI derinlikli cikarim yapamaz


## Karar #84 — CLI Split Projesi Tamamlandı (2026-06-27 21:32)

**Ne yapıldı?** ReYMeN projesinde CLI split migrasyonu 6 görevde tamamlandı:
- GÖREV 01: Split modüller bağlandı, cli.py wrapper'a dönüştü (15K→485 satır)
- GÖREV 02: ReYMeNCLI class'ı 6 mixin'e bölündü
- GÖREV 03: Voice metotları taşındı
- GÖREV 04: 41 SyntaxError → 0
- GÖREV 05: 181 test, %5→%43 coverage
- GÖREV 06: 0 gereksiz shell=True

**Neden?** Kullanıcının talebi: CLI split migrasyonu + mixin bölme
|

---

## Karar #85 — Cronjob API Tool (2026-06-28)

**Ne yapıldı?** `tools/cronjob_tool.py` oluşturuldu — Hermes cronjob() API'si ile uyumlu ReYMeN cron yönetim tool'u.

**API desteği:** create / list / update / pause / resume / remove / run
- `action="create"` → schedule + prompt/skills/script ile job oluşturur
- `action="list"` → tüm job'ları listeler
- `action="update"` → job günceller (updates sözlüğü ile)
- `action="pause"` / `action="resume"` → duraklat/devam ettir
- `action="remove"` → job siler (çıktı dizinini de temizler)
- `action="run"` → job'ı hemen tetikler (next_run_at=now)
- Schedule formatları: `"every 30m"`, `"0 9 * * *"`, `"2026-07-01T14:00"`, `"30m"`
- `no_agent=True` ile script tabanlı watchdog desteği
- Mevcut `cron/jobs.py` altyapısını kullanır (49KB, Hermes'ten)

**Neden?** Kullanıcının talebi: "Hermes bulunan Cron sistemi — cronjob() API sistemi reymen de yapalim". Mevcut `cronjob_tools.py` (HH:MM+shell=True) çok basitti.

**Alternatif?** Mevcut `cronjob_tools.py`'yi genişletmek — ama API kontratı farklıydı, ayrı dosya daha temiz.

**Doğrulama:** 11 test senaryosu (create/list/pause/resume/update/trigger/remove) başarıyla geçti. Motor.py'ye `tools.cronjob_tool` kaydı eklendi.

**Alternatif?** Split'ten vazgeçip eski cli.py (15K) ile devam etmek — kullanıcı tam çözüm istedi.

---
### Karar #31 — 5 Ajanlı Otonom Görev Çözücü Mimarisi
**Ne yapıldı?** ReYMeN'e 5 ajanlı otonom görev çözücü sistemi kuruldu: Hafıza (once_hafiza), Beceri (motor.py), Tarayıcı (run_script), Analiz (orchestrator+model_adapter), İletişim (telegram/cli).
**Neden?** ReYMeN'in kendi kendine hata çözmesi, Cline'a bağımlı kalmaması için.
**Alternatif?** Tek monolitik yapı yerine 5 ayrı sorumluluk — her biri bağımsız test edilebilir.
**Dosyalar:** reymen/core/model_adapter.py, orchestrator.py, motor.py (gorev_coz + hatadan_kurtul)
---
### Karar #32 — SQLite Hafıza + TTL + Soyut İmza + Doğrulamalı Kayıt
**Ne yapıldı?** reymen/core/ogrenme.py SQLite tabanlı hata→çözüm hafızası. TTL=30gün (basari_sayisi>=3 muaf), soyut imza (path/değer atlar), doğrulamalı kayıt (LLM fix'i çalışırsa kaydet). motor.py'de script_calistir() ile entegre.
**Neden?** Eski JSONL concurrent write korumasızdı. FTS5 her ortamda yok. LLM halüsinasyonunu doğrulamalı kayıtla önler.
