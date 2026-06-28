---
skill_id: 7f85d7480362
usage_count: 1
last_used: 2026-06-16
---
# Run a scan command
"$VBOX" controlvm "$VM" keyboardputstring "sudo nmap -sn 192.168.0.0/24"
"$VBOX" controlvm "$VM" keyboardputstring $'\n'