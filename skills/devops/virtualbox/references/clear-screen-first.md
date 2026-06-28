---
skill_id: d54fc61c3715
usage_count: 1
last_used: 2026-06-16
---
# Clear screen first
"$VBOX" controlvm "$VM" keyboardputstring "clear"
"$VBOX" controlvm "$VM" keyboardputstring $'\n'
sleep 1