
> **Kategori:** Windows

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Kali ajanı |
| **Ne?** | Windows Automation_Kali Vbox Klavye Iletimi_References_Adim 3 Detayli Tarama |
| **Nerede?** | Windows/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

# Adim 3: Detayli tarama
"C:\Program Files/Oracle/VirtualBox/VBoxManage.exe" controlvm "kal" keyboardputstring "sudo nmap -sn 192.168.0.0/24" && "C:\Program Files/Oracle/VirtualBox/VBoxManage.exe" controlvm "kal" keyboardputstring $'\n'
sleep 5
```