
> **Kategori:** AI_ML

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Tüm ajanlar |
| **Ne?** | Ecc_Flox Environments_References_Hooks And Profile |
| **Nerede?** | AI_ML/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

## Hooks and Profile

### Hooks — Non-Interactive Setup

Hooks run on every activation. Keep them fast and idempotent. Rule of thumb: **if it should happen automatically, put it in `[hook]`; if the user should be able to type it, put it in `[profile]`.**

```toml
[hook]
on-activate = """
  setup_database() {
    if [ ! -d "$FLOX_ENV_CACHE/pgdata" ]; then
      initdb -D "$FLOX_ENV_CACHE/pgdata" --no-locale --encoding=UTF8
    fi
  }
  setup_database
"""
```

### Profile — Interactive Shell Configuration

Profile code is available in the user's shell session.

```toml
[profile]
common = """
  dev() { npm run dev; }
  test() { npm run test -- "$@"; }
"""
```