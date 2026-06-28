---
skill_id: eea521abedf6
usage_count: 1
last_used: 2026-06-16
---
# Önce JavaNotes submodule'ünü işle
if [ -f JavaNotes/.git ]; then
  cd JavaNotes
  git add -A 2>/dev/null
  git commit -m "Auto backup submodule $(date +%Y-%m-%d_%H:%M)" 2>/dev/null
  GIT_TERMINAL_PROMPT=0 git push origin main 2>/dev/null &
  cd ..
fi