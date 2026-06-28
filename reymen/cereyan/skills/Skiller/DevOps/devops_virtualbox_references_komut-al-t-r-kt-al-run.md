
> **Kategori:** DevOps

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Tüm ajanlar |
| **Ne?** | Devops_Virtualbox_References_Komut Al T R Kt Al Run |
| **Nerede?** | DevOps/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

# Komut çalıştır + çıktı al (run)
r = subprocess.run([
    vbox, "guestcontrol", vm, "run",
    "--exe", "/usr/bin/ls",
    "--username", user, "--password", pwd,
    "--wait-stdout", "--", "-la", "/usr/bin/",
], env=env, capture_output=True, text=True)
print(r.stdout)
```