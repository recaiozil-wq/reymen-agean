
> **Kategori:** Windows

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Kali ajanı |
| **Ne?** | Windows Automation_Kali Vbox Klavye Iletimi_References_Nemli I Lk Tercih Guest Control Olmal |
| **Nerede?** | Windows/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

## ÖNEMLİ — İlk Tercih Guest Control Olmalı

Terminal açmak veya komut çalıştırmak için **önce guestcontrol dene**, keyboardputstring sonra:
- GuestControl: `VBoxManage guestcontrol "kal" start --exe "/usr/bin/qterminal" --username kali --password kali`
- GuestControl çalışmazsa (Guest Additions yoksa) keyboardputstring'e düş
- Detaylar için `virtualbox` skill'inde "Guest Control" bölümüne bak

VirtualBox VM'deki Kali Linux terminaline klavye girisini VBoxManage ile yap.