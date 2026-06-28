
> **Kategori:** DevOps

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Tüm ajanlar |
| **Ne?** | Devops_Virtualbox_References_Quick Paths |
| **Nerede?** | DevOps/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

## Quick Paths

### 1. Check VM status
```bash
VBoxManage = r"C:\Program Files\Oracle\VirtualBox\VBoxManage.exe"
subprocess.run([VBoxManage, "showvminfo", VM_NAME, "--machinereadable"])