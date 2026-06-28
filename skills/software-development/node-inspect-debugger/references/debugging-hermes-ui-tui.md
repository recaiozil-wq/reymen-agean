---
skill_id: e128086d4692
usage_count: 1
last_used: 2026-06-16
---
## Debugging ReYMeN ui-tui

The TUI is built Ink + tsx. Two common scenarios:

### Debugging a single Ink component under dev

`ui-tui/package.json` has `npm run dev` (tsx --watch). Add `--inspect-brk` by running tsx directly:

```bash
cd /home/bb/hermes-agent/ui-tui
npm run build    # produce dist/ once so transpile isn't needed on first load
node --inspect-brk dist/entry.js