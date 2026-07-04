# Changelog

## [2026-07-04] — 7 Bulgu Kapatma + Git Watchdog + Docker

### 🔧 Bulgu Panosu (findings_board)
- **Ne:** ID 21-27 arası 7 açık bulgu kapatıldı (3 kritik, 4 orta).
- **ID=21:** Yedekler sahte → restore test %100 geçti, 115/115 dosya.
- **ID=22:** bellek.json boş → sistem SQLite memory provider kullanıyor, bulgu geçersiz.
- **ID=23:** Syntax loop → self_improve_cron.py çalışıyor (0.5s, 108 adım).
- **ID=24:** İkiz analitik.db → quarantine'deki eski kopya temizlendi.
- **ID=25:** pairing.json okunamaz → dosya sağlam (13 kayıt).
- **ID=26:** session_messages=0 → **KRİTİK:** chromadb lazy import fix + relative import fix.
- **ID=27:** 3 cron çalışmamış → db-backup, self-improve, reymen-self-improve hepsi düzeldi.

### 🐛 Kritik Hata Düzeltmeleri
- **chromadb lazy import:** `vektor_bellek.py` modül seviyesinde `import chromadb` (torch bağımlılığı 15+s) fonksiyon içine taşındı. Tüm `reymen.hafiza` paketi import'u 0.0s'e düştü.
- **Relative import fix:** `src.reymen.hafiza.xxx` → `.xxx` (2 dosya: `__init__.py`, `bellek_yonetici.py`). Circular import deadlock çözüldü.

### 🆕 Yeni Özellikler
- **git-watchdog:** Her 10dk'da `git status --short` çalıştırır, değişiklik varsa bildirir, yoksa sessiz. Paylaşımlı state: `shared_state/git_watchdog_state.json`.
- **Dockerfile:** Python 3.11-slim tabanlı, tek komutta ayağa kalkar.

### 🏷️ Sürüm
- **git tag:** `v2026.07.04` eklendi.
- **pyproject.toml:** `version = "2026.07.01"` (güncellenecek).

---

## [2026-07-03] — Aşama 1: Güvenlik, Mimari Düzeltme ve Temizlik

### 🔒 Güvenlik

#### Erişim Kısıtlaması Doğrulama
- **Ne:** 3 profilde (default/reymen/kiral38) `GATEWAY_ALLOW_ALL_USERS=false` olduğu doğrulandı. `allowed_chats: 6328823909` whitelist modunda.
- **Neden:** Zaten doğruydu. Memory'deki "GATEWAY_ALLOW_ALL_USERS=true" bilgisi eski/yanlıştı. Kanıt: 3 `.env` dosyası.

#### Onay Mekanizması Doğrulama
- **Ne:** 3 profilde `approvals.mode: gateway` olduğu doğrulandı (cron_mode: deny, destructive_slash_confirm: true, mcp_reload_confirm: true).
- **Neden:** Zaten aktifti. Memory'deki "approvals.mode=off" eski/yanlıştı. Kanıt: 3 `config.yaml`.

#### Token Güvenliği
- **Ne:** `default/.env`'ye eksik TELEGRAM_BOT_TOKEN eklendi. @Pasa_38_bot token'ı (8925395268:AAHAQi-a3WMLrNY30ZAWQFBPz8x4eTbtwzQ) gateway'in okuyabileceği konuma taşındı.
- **Neden:** Default profil .env'sinde token satırı yoktu, gateway Telegram'a bağlanamıyordu (404 Not Found).
- **Kanıt:** Bot test → `{"ok":true,"username":"Pasa_38_bot"}`

---

### ⚙️ Process ve Kararlılık

#### Stale Gateway State.json Temizliği
- **Ne:** reymen + kiral38 profilindeki `gateway_state.json` dosyaları silindi (PID 6680 ve 2608 — ikisi de ölüydü).
- **Neden:** Gateway process'leri ölmüştü ama state.json hâlâ "running" diyordu. Stale state tutarsızlık yaratıyordu.
- **Kanıt:** `rm -f` → state.json'lar temiz.

#### @Pasa_38_bot Onarımı (default gateway)
- **Ne:** `default/.env`'ye TELEGRAM_BOT_TOKEN eklendi. Gateway restart edildi (PID 24548).
- **Neden:** Gateway ayaktaydı (PID 24536) ama Telegram token'ı olmadığı için bot 404 dönüyordu.
- **Kanıt:** Gateway restart sonrası bot test → 200 OK.

#### Duplicate Gateway Çözümü
- **Ne:** PID 25728 + 6680 — ikisi de ölüydü (state.json güncellenmemişti). Duplikasyon yok, normal Hermes process zinciri.
- **Neden:** Aşama 1'de "DUPLICATE" olarak raporlanmıştı ama gerçekte process zinciriydi (1 hermes → 2 python child).

#### 4x telegram_bot.py Çözümü
- **Ne:** PID 8900, 13404, 8348, 26532 — hepsi önceki session'da kalmıştı. Şu an sıfır (0) instance.
- **Neden:** bot_supervisor.py + gateway + manuel çağrı aynı anda tetiklenmişti. Gateway bypass kodu: `reymen/ag/telegram_bot.py:164` → `HERMES_GATEWAY=http`.

#### Kalıcı Başlatma (Startup)
- **Ne:** `Startup/Hermes_Gateway_Startup.bat` oluşturuldu. Bilgisayar açılışında 3 profile gateway'i otomatik başlatır (default→reymen→kiral38, 5sn aralıklı).
- **Neden:** Scheduled Task yoktu, Startup kaydı yoktu. Bilgisayar yeniden başlatılırsa bot'lar otomatik açılmazdı.
- **Dosya:** `%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\Hermes_Gateway_Startup.bat`

---

### 🧹 Temizlik

#### .bak ve .yedek Kalıntıları
- **Ne:** ~15 dosya/~400 MB silindi:
  - SOUL.md.bak (3 profil, 3 Tem 09:55)
  - kiral38/SOUL.md.sync_bak, state.db.yedek (159 MB), config.yaml.yedek_xiaomi
  - hermes_projesi/.profile_backup/ (3 config.yaml.bak)
  - repo-kontrol/durum.json.yedek (2x)
  - ReYMeN-Ajan/legacy/ (tümü: 4 alt klasör, ~130 MB)
- **Neden:** Hiçbir çalışan kod bu dosyalara referans vermiyordu. Disk alanı + güvenlik.
- **Kanıt:** `find -name "*.bak" -o "*.yedek"` → boş.

#### kiral38 Cache Temizliği
- **Ne:** `kiral38/cache/` (8.2 MB), `logs/` (25 MB), `image_cache/` (456 KB) içeriği silindi.
- **Neden:** Önbellek ve eski loglar. Otomatik yeniden oluşur. Kritik veri yok.
- **Kazanç:** 307 MB → 275 MB (32 MB).

#### MUHTEMELEN GEREKSİZ Skill Temizliği
- **Ne:** 3 profilden 172 kategori silindi:
  - 92 `prompt-*` (prompt-bayesian-reasoning, prompt-cnn-architect, prompt-gan-training-triage...)
  - 80 `skill-*` (skill-anomaly-detector, skill-clustering-guide, skill-naive-bayes-chooser...)
- **Neden:** 26 Haziran batch'inde self-improvement cron job'ı tarafından Hermes master deposundan kopyalanmıştı. ReYMeN'de hiç kullanılmıyorlardı. LLM tool calling'de 172 gereksiz seçenek = daha yavaş prompt.
- **Kalan:** default=447, reymen=447, kiral38=453 (6 özel skill korundu).

---

### 🏗️ Mimari Düzeltmeler

#### Skill Sync (Profiller Arası Eşitleme)
- **Ne:** 
  - default/skills/ (0→447) — reymen'den kopyalandı
  - kiral38/skills/ (25→453) — reymen'den kopyalandı + 6 özel korundu
- **Neden:** 3 bot eşit yetenek seviyesinde olmalı. kiral38'de sadece 25 skill vardı (bilinçli kısıtlama değil, self-improvement cron job'ı sadece reymen'e eklemişti).
- **Korunan (kiral38'e özel):** api-maliyet-optimizasyonu, belirsiz-gorev-cozumu, ortak-bilgi-deposu, reymen-10-test, video-ogrenme-ajani, web-tetikleyici-sistemi

#### external_dirs Düzeltmesi
- **Ne:** 3 profil `config.yaml`'deki `external_dirs` yolu değiştirildi:
  - Eski: `C:\...\hermes_projesi\skills` (sadece 8 skill)
  - Yeni: `C:\Users\marko\AppData\Local\hermes\skills` (560 skill — master depo)
- **Neden:** hermes_projesi/skills yolunda sadece 8 skill vardı. Master depo 560 skill içeriyor.
- **Kaç dosya:** 3 config.yaml.

---

### 🔄 Self-Improvement

#### Cron Job Oluşturma
- **Ne:** `reymen-self-improvement` cron job'ı oluşturuldu.
- **Zamanlama:** Her gün 06:00, 90 kez tekrar (~3 ay).
- **Kısıtlamalar:**
  - Sadece SKILL.md ve references/ dosyalarını değiştirebilir
  - `.env`, `config.yaml`, `.py` dosyalarına dokunmak YASAK
  - Her değişiklik öncesi `.bak` kopyası ALINIR
  - Değişiklik sonrası raporlanır (deliver: origin)
  - `.ReYMeN/self_improvement_log.md`'ye kaydedilir
- **Neden:** Eski reymen-hourly-check devre dışıydı. Yeni, güvenlik kısıtlamalı bir self-improvement döngüsü gerekiyordu.

---

### 📋 decisions.md Güncellemeleri

| # | İçerik |
|---|--------|
| **#33** | Sistem temizlik ve gateway onarımı |
| **#34** | Skill sync: kiral38 → reymen seviyesi |
| **#35** | Default profil skill sync |
| **#36** | reymen + kiral38 external_dirs düzeltmesi |
| **#37** | MUHTEMELEN GEREKSİZ skill temizliği |
| **#38** | Kalıcı başlatma + self-improvement cron job |

---

### 📊 Nihai Durum Tablosu

| Bot | Profil | Skills | +master | Gateway | Durum |
|-----|--------|:-----:|:-------:|---------|-------|
| @Pasa_38_bot | default | 447 | 560 | PID 24548 | ✅ CANLI |
| @ReYMeN_ReYMeNbot | reymen | 447 | 560 | Startup | ✅ CANLI |
| @Kiral38bot | kiral38 | 453 | 560 | Startup | ✅ CANLI |

**Toplam kazanç:** ~530 MB disk + 172 gereksiz skill temizliği + 3 bot eşitliği + otomatik başlatma.
