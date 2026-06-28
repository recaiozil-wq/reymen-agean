---
skill_id: 49d6331fcd80
usage_count: 1
last_used: 2026-06-16
---
## Recommended Workflow

1. Inspect VM state (`showvminfo --machinereadable`). Kullanıcıya sorma, direkt yap.
2. If powered off: start headless, wait 30-60s for boot; or GUI with `--type gui` if user wants to see it
3. If need to run something inside VM: **prefer guestcontrol** (`run` with `--wait-stdout`) over keyboardputstring
4. If need to open terminal in VM GUI: **prefer guestcontrol** (`start --exe /usr/bin/qterminal`) over Ctrl+Alt+T
5. Fallback: keyboardputstring/scancode only if guestcontrol unavailable or Guest Additions missing
6. Verify networking: `showvminfo` for NICs, `guestproperty get` for IP
7. Test connection (SSH `nc` probe or `ssh -o ConnectTimeout=5`)
8. If all else fails: use screenshot + visual analysis to confirm boot state, then guide user