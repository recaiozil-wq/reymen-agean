
> **Kategori:** Windows

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Kali ajanı |
| **Ne?** | Windows Automation_Kali Linux Remote_References_Sudo Nbellek Is Tma Her Oturumda I Lk Adim |
| **Nerede?** | Windows/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

## Sudo Önbellek Isıtma (HER OTURUMDA İLK ADIM)

Kali'ye SSH bağlanır bağlanmaz sudo önbelleğini ısıtmak için:

```bash
sshpass -p 'kali' ssh -o StrictHostKeyChecking=no kali@192.168.0.19 'echo kali | sudo -S -v && echo "SUDO_CACHE_OK"'
```

Bu adım otomatik cron job ile her gün 08:00'de çalışır (cron job ID: fb150a1866f8).
Eğer cron çalışmamışsa, SSH komutundan önce manuel çalıştır.

**Kontrol:** sshpass Kali'de kurulu değilse `sudo apt-get install -y sshpass` ile kur.