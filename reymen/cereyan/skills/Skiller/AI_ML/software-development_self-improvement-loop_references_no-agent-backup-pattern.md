---
name: software-development_self-improvement-loop_references_no-agent-backup-pattern
description: no_agent Cron Backup Pattern
title: "Software Development Self Improvement Loop References No Agent Backup Pattern"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | no_agent Cron Backup Pattern |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# no_agent Cron Backup Pattern

## Ne İşe Yarar
Backup gibi tekrarlı shell işlerini **LLM harcamadan** çalıştırmak.
`no_agent=True` modu: script çıktısını doğrudan kullanıcıya iletir, aracı (agent) başlatılmaz.

## Avantaj
- **Sıfır token tüketimi** — LLM çağrılmaz
- **Hızlı** — script doğrudan çalışır
- **Sessiz** — başarılı çalışmada çıktı yoksa sessiz geçer
- **Hata bildirimi** — hata olursa otomatik bildirilir

## Kullanım

### 1. Script oluştur
```bash
# ~/AppData/Local/hermes/profiles/kiral38/scripts/memory_backup.sh
#!/bin/bash
PROJE="/c/Users/marko/Desktop/Reymen Proje/hermes_projesi"
REMOTE="https://github.com/Watcher-Hermes/hermes-memory-backup.git"
TARIH=$(date '+%Y-%m-%d_%H-%M')

rm -rf /tmp/backup && mkdir -p /tmp/backup
cp -r "$PROJE/.ReYMeN" /tmp/backup/
cd /tmp/backup && git init -q && git add -A
git commit -q -m "backup $TARIH" --allow-empty
git remote add origin "$REMOTE" && git push -f origin master 2>&1

echo "OK backup $TARIH"
```

### 2. Cron job oluştur
```python
cronjob(action='create',
    name='memory-backup-daily',
    schedule='30 0 * * *',    # her gün 00:30
    script='memory_backup.sh', # ~/AppData/.../scripts/ altında
    no_agent=True)             # LLM çağrılmaz!
```

## Önemli Kurallar

| Kural | Açıklama |
|-------|----------|
| Script yolu | `profiles/kiral38/scripts/` altında olmalı |
| .sh → bash | `.sh`/`.bash` uzantısı → bash ile çalışır |
| .py → python | Diğer uzantılar → Python ile çalışır |
| Sessiz başarı | Çıktı boşsa kullanıcıya hiçbir şey gitmez |
| Hata bildirimi | Non-zero exit → uyarı gider |
| Çıktı formatı | İlk satır = özet, kullanıcıya o gider |

## Kullanım Alanları
- Git push (memory/full backup)
- Sistem sağlık kontrolü
- Disk/memory watchdog
- CI poller
- Dosya temizlik/senkronizasyon
