# Skills Dizin Yapisi — Path Cleanup

## Merkezi Dizin
**`reymen/cereyan/skills/`** — tek merkezi skills dizini (kategorize edilmis yapi).

## Eski/Yedek Dizinler (artik kullanilmiyor)
| Dizin | Durum | Aciklama |
|-------|-------|----------|
| `skills/` | YEDEK | Duz (flat) .md dosyalari, cogu merkezi dizinde zaten var |
| `.ReYMeN/skills/` | BOS | Hub sistemi icin ayrilmis, su an bos |
| `hermes_legacy/skills/` | LEGACY | Eski yedek, otomatik taranmiyor |
| `reymen/cereyan/.ReYMeN/skills/` | TEST | Test skill'leri ve index-cache |
| `reymen/hafiza/.ReYMeN/skills/` | MINIMAL | 17 .md, cogu eski |

## Sync Komutu
```bash
# Merkezi dizin + root skills/ senkronizasyonu
python -c "from reymen.cereyan.fix_skills_path import *; sync_all()"

# Durum raporu
python -c "from reymen.cereyan.fix_skills_path import *; durum_bildir()"
```

## Auto-Activation (yeni)
Kullanici sorgusuna gore ilgili skill'ler otomatik aktif edilir:
- `conversation_loop.py` -> `sorgudan_aktif_et()` (OnceHafiza kontrolunden sonra)
- SkillLibrary SQLite DB: `reymen/cereyan/.ReYMeN/skill_library.db`

## CLI Fix
`/skills` slash command artik `cli_commands.tool_commands` uzerinden calisir.
`cli_mixin_skillstools.py`'daki kirik `ChatConsole()` import'u duzeltildi.
