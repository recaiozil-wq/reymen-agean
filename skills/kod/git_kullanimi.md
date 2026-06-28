---
title: Git Versiyon Kontrolü
description: Git komutları, commit, push, branch yönetimi
tags: [git, versiyon, commit, branch]
---

## Repo durumu
KOMUT_CALISTIR "git status"
KOMUT_CALISTIR "git log --oneline -10"

## Değişiklik kaydet
KOMUT_CALISTIR "git add -A && git commit -m \"güncelleme: açıklama\""

## Branch oluştur ve geç
KOMUT_CALISTIR "git checkout -b yeni-ozellik"

## Değişiklik gör
KOMUT_CALISTIR "git diff HEAD~1"

## Uzak repoya gönder
KOMUT_CALISTIR "git push origin main"

## Conflict çöz
PYTHON_CALISTIR "
import subprocess
sonuc = subprocess.run(['git', 'status'], capture_output=True, text=True)
conflict = [s for s in sonuc.stdout.split('\n') if 'conflict' in s.lower() or 'both' in s.lower()]
print('\n'.join(conflict) if conflict else 'Conflict yok')
"
