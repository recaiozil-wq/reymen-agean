
> **Kategori:** AI_ML

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Tüm ajanlar |
| **Ne?** | Ecc_Flox Environments_References_Core Concepts |
| **Nerede?** | AI_ML/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

## Core Concepts

Flox environments are defined in `.flox/env/manifest.toml` and activated with `flox activate`. The manifest declares packages, environment variables, setup hooks, and shell configuration — everything needed to reproduce the environment anywhere.

**Key paths:**
- `.flox/env/manifest.toml` — Environment definition (commit this)
- `$FLOX_ENV` — Runtime path to installed packages (like `/usr` — contains `bin/`, `lib/`, `include/`)
- `$FLOX_ENV_CACHE` — Persistent local storage for caches, venvs, data (survives rebuilds)
- `$FLOX_ENV_PROJECT` — Project root directory (where `.flox/` lives)