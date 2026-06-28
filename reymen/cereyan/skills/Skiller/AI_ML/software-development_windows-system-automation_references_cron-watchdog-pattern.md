---
name: software-development_windows-system-automation_references_cron-watchdog-pattern
description: Cron Watchdog Pattern (no_agent=True)
title: "Software Development Windows System Automation References Cron Watchdog Pattern"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Cron Watchdog Pattern (no_agent=True) |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Cron Watchdog Pattern (no_agent=True)

## Ne Zaman Kullanılır

- Periyodik backup/sync görevleri (disk, git, config)
- Bağlantı/sağlık kontrolleri
- Herhangi bir "LLM gerekmez, script çalıştır, çıktıyı ilet" durumu

## Avantajları

- **Token harcamaz** — LLM çağrısı yok
- **Daha hızlı** — script doğrudan çalışır
- **Sessiz mod** — boş stdout = bildirim gitmez
- **Non-zero exit** = hata bildirimi

## Oluşturma

```python
cronjob(
    action='create',
    name='otomatik-yedekleme',
    schedule='0 4 * * *',        # her gece 04:00
    script='auto_backup.py',      # scripts/ altındaki dosya
    no_agent=True,                # LLM çağırmaz
    deliver='telegram:6328823909' # sonucu Telegram'a gönder
)
```

## Script Yazma Kuralları

- `C:\Users\marko\AppData\Local\hermes\scripts\` altına koy
- `.py` uzantısı → Python ile çalışır, `.sh`/`.bash` → bash ile
- stdout doğrudan Telegram'a iletilir
- Sessiz geçiş için: değişiklik yoksa hiçbir şey yazdırma
- Token/şifre gibi hassas verileri `.env`'den oku

## Örnek: auto_backup.py

```python
#!/usr/bin/env python3
"""Hermes + Obsidian vault -> GitHub"""
import subprocess, os
from datetime import datetime

HERMES_DIR = r"C:\Users\marko\AppData\Local\hermes"
VAULT_DIR = r"C:\Users\marko\OneDrive\Belgeler\Obsidian Vault"
ENV_PATH = r"C:\Users\marko\AppData\Local\hermes\.env"
GITHUB_USER = "asdafgf"

def get_token():
    if not os.path.exists(ENV_PATH): return None
    with open(ENV_PATH) as f:
        for line in f:
            if line.startswith('GITHUB_TOKEN='):
                val = line.split('=',1)[1].strip().strip('"').strip("'")
                return val if val and val != '***' else None
    return None

def run(cmd, cwd):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=120, shell=True)
    return r.returncode, r.stdout.strip(), r.stderr.strip()

def backup(path, name, repo_name, token):
    remote = f"https://{GITHUB_USER}:{token}@github.com/{GITHUB_USER}/{repo_name}.git"
    # ensure repo exists
    code, _, _ = run("git rev-parse --git-dir", path)
    if code != 0:
        run("git init", path)
        run("git branch -M main", path)
        run(f"git remote add origin {remote}", path)
        run("git add -A", path)
        run('git commit -m "initial setup" --allow-empty', path)
    run(f"git remote set-url origin {remote}", path)

    code, out, _ = run("git status --porcelain", path)
    if not out.strip():
        return f"⏭️ Temiz"

    files = len([l for l in out.split('\n') if l.strip()])
    run("git add -A", path)
    date = datetime.now().strftime("%Y-%m-%d %H:%M")
    code, _, err = run(f'git commit -m "backup {name}: {date}"', path)
    if code != 0: return f"❌ {err[:150]}"
    code, _, err = run("git push origin main", path)
    if code != 0: return f"❌ Push: {err[:150]}"
    return f"✅ {files} dosya"

if __name__ == "__main__":
    token = get_token()
    if not token:
        print("⏸️ GITHUB_TOKEN .env'de yok. Backup atlandı.")
        exit(0)
    print(f"🔄 {datetime.now().strftime('%H:%M')}")
    print(f"📦 Hermes: {backup(HERMES_DIR, 'Hermes', 'hermes-backup', token)}")
    print(f"📓 Vault:  {backup(VAULT_DIR, 'Vault', 'obsidian-vault', token)}")
```
