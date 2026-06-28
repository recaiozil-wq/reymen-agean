
> **Kategori:** DevOps

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Tüm ajanlar |
| **Ne?** | Devops_Virtualbox_References_Gui Uygulamas Ba Lat Start |
| **Nerede?** | DevOps/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

# GUI uygulaması başlat (start)
subprocess.run([
    vbox, "guestcontrol", vm, "start",
    "--exe", "/usr/bin/qterminal",
    "--username", user, "--password", pwd
], env=env)