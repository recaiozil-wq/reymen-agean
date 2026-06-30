# ReYMeN Skills (Built-in)

Bu klasör Hermes built-in skill sisteminin ReYMeN karşılığıdır.

## Konum
- **Ana skill deposu**: `C:\Users\marko\Desktop\Reymen Proje\ReYMeN-Ajan\skills\` (6798 dosya)
- **Format**: SKILL.md (YAML frontmatter + markdown body)
- **Yönetim**: `reymen/cereyan/skill_library.py`, `skill_activator.py`, `tools/skills_hub.py`

## Bağlantı
- Hermes config'inde `skills.dir: .ReYMeN/skills` tanımlı
- Hermes config'inde `skills.external_dirs` ile proje kökü `skills/` yolu eklenebilir
- Motor: `reymen/cereyan/skill_library.py` ile FTS5 index üzerinden yönetilir
