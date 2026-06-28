---
skill_id: 5520f1be9ee0
usage_count: 1
last_used: 2026-06-16
---
# Başarısızsa PAT dene
if [ $? -ne 0 ]; then
  PAT=$(grep "^GITHUB_TOKEN=" /c/Users/marko/AppData/Local/hermes/.env | head -1 | cut -d= -f2)
  if [ -n "$PAT" ] && [ "$PAT" != "***" ]; then
    git remote set-url origin "https://Watcher-Hermes:$PAT@github.com/Watcher-Hermes/obsidian-vault.git"
    GIT_TERMINAL_PROMPT=0 git push origin "$BRANCH"
  fi
fi
```

### 3. Telegram Bildirimi

```python