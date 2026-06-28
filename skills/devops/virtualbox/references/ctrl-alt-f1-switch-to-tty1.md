---
skill_id: de6080668aa7
usage_count: 1
last_used: 2026-06-16
---
# Ctrl+Alt+F1 (switch to TTY1)
sc(['1d', '38', '05'])
time.sleep(0.1)
sc(['85', 'b8', '9d'])
```

**Common Linux VM keyboard shortcuts:**

| Shortcut | Action | Scancode (press then release) |
|----------|--------|-------------------------------|
| Ctrl+Alt+T | Open terminal (GNOME/KDE/Xfce) | `1d 38 14` → `94 b8 9d` |
| Ctrl+Alt+F1..F6 | Switch to TTY1..TTY6 | `1d 38 05..0a` → `85..8a b8 9d` |
| Ctrl+Alt+F7 | Switch back to GUI | `1d 38 07` → `87 b8 9d` |
| Super | GNOME Activities / KDE menu | `5b` → `db` |
| Alt+F4 | Close active window | `38 3e` → `be b8` |
| Ctrl+C | Send SIGINT | `1d 2e` → `ae 9d` |
| Ctrl+Shift+T | New terminal tab | `1d 2a 14` → `94 aa 9d` |

**When to use scancodes vs. keyboardputstring:**
- **keyboardputstring** → typing text commands, single-line input, Enter via `$'\n'`
- **keyboardputscancode** → keyboard shortcuts (Ctrl+Alt+T), modifier-only combos, function keys, arrow key navigation

**Common use cases:**
```bash