---
skill_id: ab3fbee353cc
usage_count: 1
last_used: 2026-06-16
---
# Echo a separator
"$VBOX" controlvm "$VM" keyboardputstring "echo ===== TARAMA BASLIYOR ====="
"$VBOX" controlvm "$VM" keyboardputstring $'\n'
sleep 1