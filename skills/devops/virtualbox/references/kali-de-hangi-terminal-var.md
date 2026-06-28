---
skill_id: 4a8e0290af2b
usage_count: 1
last_used: 2026-06-16
---
# Kali'de hangi terminal var?
MSYS2_ARG_CONV_EXCL="*" "C:\Program Files\Oracle\VirtualBox\VBoxManage.exe" \
  guestcontrol "kal" run --exe "/usr/bin/ls" --username kali --password kali \
  --wait-stdout -- -la /usr/bin/ | grep -i term