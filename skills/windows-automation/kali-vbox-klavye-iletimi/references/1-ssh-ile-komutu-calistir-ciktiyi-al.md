---
skill_id: 3b39929f241b
usage_count: 1
last_used: 2026-06-16
---
# 1. SSH ile komutu calistir, ciktiyi al
CIKTI=$(sshpass -p 'kali' ssh kali@192.168.0.19 'sudo nmap -sn 192.168.0.0/24 2>&1')