---
skill_id: b3ff7ebe5a6a
usage_count: 1
last_used: 2026-06-16
---
## SSH ile Kali'ye Bağlanma (Kalıcı şifresiz sudo)
Kali'de şifresiz sudo ayarı yapıldıktan sonra SSH komutlarında `sudo -S` bypass'ına gerek kalmaz:
```python
cmd[-1] = "sudo arp-scan -l 2>&1"
```