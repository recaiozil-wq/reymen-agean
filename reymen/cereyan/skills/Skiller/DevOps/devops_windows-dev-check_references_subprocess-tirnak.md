
> **Kategori:** DevOps

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Windows ajanı |
| **Ne?** | Devops_Windows Dev Check_References_Subprocess Tirnak |
| **Nerede?** | DevOps/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

# KIRILMA KOŞULU 8 — Subprocess Tırnak Sorunu

**Tetikleyici:** `subprocess.run(komut, shell=True)`

**Kırılma:** `shell=True` Windows'ta `cmd.exe /c "komut"` çağırır. Eğer komut içinde çift tırnak varsa, cmd.exe bunları yorumlar ve argümanlar bozulur.

**Çözüm:**
```python
# YANLIŞ:
subprocess.run(f'pip install "{paket}"', shell=True)

# DOĞRU:
subprocess.run(["pip", "install", paket], shell=False)

# shell=True ZORUNLU ise:
subprocess.run(f'pip install "{paket}"', shell=True)
# ama paket adında tırnak olmadığından emin ol
```
