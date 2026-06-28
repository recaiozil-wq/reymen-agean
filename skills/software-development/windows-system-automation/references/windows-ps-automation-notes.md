---
skill_id: 9b2dfb8a9042
usage_count: 1
last_used: 2026-06-16
---
# Windows PowerShell UI Automation Notes (Session 2026-06-02)

- Confirmed PowerShell mouse move worked: `Add-Type -AssemblyName System.Windows.Forms` + cursor position assignment.
- Key fix: inline PowerShell commands with `$` often break when invoked from bash/MSYS; prefer writing a `.ps1` and running `powershell -ExecutionPolicy Bypass -File <path>`.
- Screenshot path: `C:\Users\marko\AppData\Local\hermes\scripts\screen.png`
- Terminal command used:
  - `printf '%s\n' '...' > C:/Users/marko/AppData/Local/hermes/scripts/move_mouse.ps1 && powershell -ExecutionPolicy Bypass -File C:/Users/marko/AppData/Local/hermes/scripts/move_mouse.ps1`
- Approved modality: this user wants visible interactive confirmations (cursor actually moves), not just console output.
