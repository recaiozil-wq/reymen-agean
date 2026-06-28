
> **Kategori:** AI_ML

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Tüm ajanlar |
| **Ne?** | Ecc_Flox Environments_References_Gnu Tools On Macos Where Bsd Defaults Differ |
| **Nerede?** | AI_ML/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

# GNU tools on macOS (where BSD defaults differ)
coreutils.pkg-path = "coreutils"
coreutils.systems = ["x86_64-darwin", "aarch64-darwin"]
```

### Resolving Package Conflicts

When two packages install the same binary, use `priority` (lower number wins):

```toml
[install]
gcc.pkg-path = "gcc12"
gcc.priority = 3

clang.pkg-path = "clang_18"
clang.priority = 5               # gcc wins file conflicts
```

Use `pkg-group` to group packages that should resolve versions together:

```toml
[install]
python.pkg-path = "python311"
python.pkg-group = "python-stack"

pip.pkg-path = "python311Packages.pip"
pip.pkg-group = "python-stack"    # Resolves together with python
```