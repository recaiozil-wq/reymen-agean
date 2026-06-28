---
skill_id: 7a5027b6fdf5
usage_count: 1
last_used: 2026-06-16
---
# SSH başarısızsa HTTPS+PAT dene
if [ $? -ne 0 ]; then
  PAT=$(grep "^GITHUB_TOKEN=" /c/Users/marko/AppData/Local/hermes/.env | head -1 | cut -d= -f2)
  if [ -n "$PAT" ] && [ "$PAT" != "***" ]; then
    git remote set-url origin "https://Izleyici-ReYMeN:$PAT@github.com/Izleyici-ReYMeN/hermes-skills.git"
    GIT_TERMINAL_PROMPT=0 git push origin master 2>/dev/null || GIT_TERMINAL_PROMPT=0 git push origin main 2>/dev/null
  fi
fi
```

### 2. Obsidian Vault Yedek

```bash
cd "/c/Users/marko/OneDrive/Belgeler/Obsidian Vault"