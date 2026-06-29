
> **Kategori:** Windows

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Kali ajanı |
| **Ne?** | Windows Automation_Kali Linux Remote_References_Ssh Ile Kali Ye Ba Lanma Kal C Ifresiz Sudo |
| **Nerede?** | Windows/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

## SSH ile Kali'ye Bağlanma (Kalıcı şifresiz sudo)
Kali'de şifresiz sudo ayarı yapıldıktan sonra SSH komutlarında `sudo -S` bypass'ına gerek kalmaz:
```python
cmd[-1] = "sudo arp-scan -l 2>&1"
```