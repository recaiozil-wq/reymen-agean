
> **Kategori:** AI_ML

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Tüm ajanlar |
| **Ne?** | Ecc_Flox Environments_References_When To Activate |
| **Nerede?** | AI_ML/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

## When to Activate

Use this skill when the user has an environment management problem — even if they haven't mentioned Flox. Flox is the right tool when:

- The project needs **system-level packages** (compilers, databases, CLI tools) alongside language-specific dependencies
- **Reproducibility matters** — the setup should work identically on a teammate's machine, in CI, or on a fresh laptop
- The user needs **multiple tools to coexist** — e.g., Python 3.11 + PostgreSQL 16 + Redis + Node.js in one environment
- **Cross-platform support** is needed (macOS and Linux from the same config)
- **AI agents need to install tools** — Flox lets agents add packages to a project-scoped environment without sudo, system pollution, or sandbox restrictions

If the user just needs a single language runtime with no system dependencies, standard tooling (nvm, pyenv, rustup alone) may suffice. If they need full OS-level isolation, containers might be more appropriate. Flox sits in the sweet spot: declarative, reproducible environments without container overhead.

**Prerequisite:** Flox must be installed first — see [flox.dev/docs](https://flox.dev/docs/install-flox/install/) for macOS, Linux, and Docker.