---
skill_id: bd0beffe66fc
usage_count: 1
last_used: 2026-06-16
---
## Sudo Önbellek Isıtma (HER OTURUMDA İLK ADIM)

Kali'ye SSH bağlanır bağlanmaz sudo önbelleğini ısıtmak için:

```bash
sshpass -p 'kali' ssh -o StrictHostKeyChecking=no kali@192.168.0.19 'echo kali | sudo -S -v && echo "SUDO_CACHE_OK"'
```

Bu adım otomatik cron job ile her gün 08:00'de çalışır (cron job ID: fb150a1866f8).
Eğer cron çalışmamışsa, SSH komutundan önce manuel çalıştır.

**Kontrol:** sshpass Kali'de kurulu değilse `sudo apt-get install -y sshpass` ile kur.