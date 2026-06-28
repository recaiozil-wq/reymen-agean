---
skill_id: d6b301ce498c
usage_count: 1
last_used: 2026-06-16
---
# 2. USB filtresi ekle (VM KAPALIYKEN)
"C:\Program Files/Oracle/VirtualBox/VBoxManage.exe" usbfilter add 0 \
  --target "kal" \
  --name "Ralink WiFi" \
  --vendorid 148f \
  --productid 2573