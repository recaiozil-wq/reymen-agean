---
skill_id: 0911148f44be
usage_count: 1
last_used: 2026-06-16
---
# Eğer .git yoksa init et
if [ ! -d .git ]; then
  git init
  git remote add origin git@github.com:Izleyici-ReYMeN/hermes-skills.git
fi

git add -A
git commit -m "Auto backup $(date +%Y-%m-%d_%H:%M)"