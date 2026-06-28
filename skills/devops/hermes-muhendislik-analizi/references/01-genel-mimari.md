---
skill_id: aa618a99efd8
usage_count: 1
last_used: 2026-06-16
---
# Bölüm 1: Genel Mimari

## ReYMeN Nedir

5 aşamalı kapalı öğrenme döngüsü:
1. Bağlam Yükleme — MEMORY.md + USER.md yüklenir
2. Araç Seçimi — 40+ araçtan seçim; 3'e kadar alt ajan paralel
3. Skill Oluşturma — Başarılı görevlerden Markdown prosedürler
4. Bellek Konsolidasyonu — FTS5 + LLM özetleme
5. Kendini İyileştirme — Eski skill'lar kullanımda güncellenir

## Temel Bileşenler
- AIAgent Loop: orkestrasyon (düşünme, araç, skill, öz-değerlendirme)
- Gateway: 20+ platform (Telegram, Discord, Slack)
- Cron Scheduler: periyodik görevler
- Tooling Runtime: 6 terminal backend (lokal, Docker, SSH, Modal)
- SQLite Persistence: oturum, bellek, skill metadata, FTS5

## 4 Bellek Katmanı
- Persistent Notes (ajan seçimi) -> SQLite + dosya
- Session History (konuşmalar) -> FTS5 indeks
- User Model (tercihler) -> Honcho diyalektik
- Procedural Memory (skill'ler) -> Markdown dosyaları

## Genel Mimari Harita

OBSIDIAN VAULT (Komuta Merkezi)
  #hermes-run etiketli notlar tetikler
        |
  watchdog (FileSystemEventHandler, 2s debounce)
        |
  ReYMeNDaemon
    |-- TelegramBot (daemon thread, long-polling)
    |-- ThreadPoolExecutor (worker threads)
              |
        _process_job()
          ParsedNote -> Flow belirleme -> filelock
              |
    learn / android / plan / ask / publish
              |
        BrainRouter (DeepSeek -> Claude -> Ollama)
              |
        _post_skill_hooks() (10 adım)
          1.code_vault    6.curiosity
          2.reflection    7.ing.ozet
          3.benchmark     8.wikilink
          4.hygiene       9.MOC yenile
          5.conflict     10.backup.commit
