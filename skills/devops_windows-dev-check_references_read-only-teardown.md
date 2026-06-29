
> **Kategori:** DevOps

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Windows ajanı |
| **Ne?** | Devops_Windows Dev Check_References_Read Only Teardown |
| **Nerede?** | DevOps/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

# KIRILMA KOŞULU 3 — Read-only Teardown

**Tetikleyici:** Test `finally` bloğu, temp dizin cleanup

**Kırılma:** Read-only dosya `os.chmod` başarısız olsa bile yazılabilir yapılmalı. Yoksa `TemporaryDirectory` silinemez.

**Çözüm (3 kademeli):**
```python
# Kademe 1: os.chmod
try:
    os.chmod(dosya, stat.S_IWUSR)
except PermissionError:
    # Kademe 2: Windows attrib -R
    import subprocess
    subprocess.run(["attrib", "-R", str(dosya)], capture_output=True, timeout=5)

# Kademe 3: temp dizin icin
shutil.rmtree(temp_dizin, ignore_errors=True)
```

**Kaynak:** `reymen-ogrenme-sistemi/references/read-only-teardown-pattern.md`
