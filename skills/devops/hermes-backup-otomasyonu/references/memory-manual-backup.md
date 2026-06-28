---
skill_id: 04a50bade34a
usage_count: 1
last_used: 2026-06-16
---
# Memory Manuel Backup — hermes-memory-backup

## Amaç

ReYMeN'in kalıcı hafızasını (MEMORY + USER PROFILE) GitHub'a manuel yedekleme.
Kronik backup'lar `hermes-backup-otomasyonu` skill'ı ile otomatik yapılır.
Bu doküman **manuel/tek seferlik** backup içindir.

## Ön Koşullar

```bash
cd /c/Users/marko
# Repo yoksa:
git clone https://github.com/Watcher-Hermes/hermes-memory-backup.git
# Repo varsa:
cd /c/Users/marko/hermes-memory-backup && git pull origin master
```

## Adımlar

### 1. MEMORY.md — Hafıza İçeriğini Çıkar

ReYMeN Agent hafızası state.db SQLite'da saklanır, direkt dosya olarak erişilemez.
Mevcut MEMORY içeriği system prompt'ta görünür (memory tool'u ile kaydedilen entry'ler).

**Yöntem:** Mevcut MEMORY içeriğini (system prompt'taki) al, `MEMORY.md` dosyasına yaz.
Obsidian vault'taki `ReYMeN/env-hermes-agent.md` dosyası da .env yedekleri için referans alınabilir.

Dosya yapısı:
```markdown
# ReYMeN Agent — Memory Backup
# Last updated: YYYY-MM-DD

entry 1
entry 2
...
```

### 2. USER.md — Kullanıcı Profilini Çıkar

Aynı yöntemle USER PROFILE içeriğini `USER.md`'ye yaz.

### 3. Commit + Push

```bash
cd /c/Users/marko/hermes-memory-backup
git add -A
git commit -m "auto-backup YYYY-MM-DD — memory + profile"
git push origin master
```

## Önemli Notlar

- **Token temizleme:** MEMORY.md'de API anahtarı, token, şifre varsa push öncesi temizle.
  GitHub Push Protection bunları algılar ve push'u bloke eder.
- **Branch adı:** `master` (main değil).
- **gh CLI auth:** `asdafgf` hesabı ile gh CLI çalışır, MCP GitHub auth çalışmaz.
- **Patlama kontrolü:** MEMORY limiti 50K, USER PROFILE limiti 5K.
  %90+ doluysa önce `memory-compaction` skill'ini çalıştır, sonra yedekle.
- **Otomatik cron zaten var:** `hermes-backup-otomasyonu` günlük 21:00'de no_agent ile
  diff+sync yapar. Manuel backup sadece acil durumlar veya büyük değişiklikler için gerekli.
