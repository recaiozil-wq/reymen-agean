---
skill_id: 6b1e0fb91ced
usage_count: 1
last_used: 2026-06-16
---
# Origin İzi Temizliği

## Ne Zaman Gerekli?

NemoClaw reposundan alınan veya ECC (Enterprise Coding Conventions) sisteminden aktarılan skill'lerde, frontmatter'da NVIDIA/ECC'ye ait izler kalabilir. Bunlar **kesinlikle temizlenmelidir.**

## Temizlenecek Alanlar

| Alan | Kaynak | Örnek |
|------|--------|-------|
| `phase:` | NVIDIA eğitim modülü | `phase: 15` |
| `lesson:` | NVIDIA ders numarası | `lesson: 18` |
| `origin:` | ECC/oh-my-agent-check | `origin: ECC` |
| `tools:` | NemoClaw araç listesi | `tools: Read, Write, Edit` |
| Tag'de `nemo` | NVIDIA ürün adı | `nemo-guardrails` → `guardrails` |

## Regex ile Toplu Temizlik

```python
import re
from pathlib import Path

repo = Path(r"skills/")
for p in repo.rglob("SKILL.md"):
    content = p.read_text(encoding="utf-8", errors="replace")
    if not content.startswith("---"):
        continue
    parts = content.split("---", 2)
    fm = parts[1]

    original = fm
    fm = re.sub(r'^phase:\s*\d+\s*\n', '', fm, flags=re.MULTILINE)
    fm = re.sub(r'^lesson:\s*\d+\s*\n', '', fm, flags=re.MULTILINE)
    fm = re.sub(r'^origin:\s*.*\n', '', fm, flags=re.MULTILINE)
    fm = re.sub(r'^tools:\s*.*\n', '', fm, flags=re.MULTILINE)
    fm = re.sub(r'\bnemo[-_]?guardrails?\b', 'guardrails', fm, flags=re.IGNORECASE)
    fm = re.sub(r'\bnemo\b', '', fm, flags=re.IGNORECASE)
    fm = re.sub(r'\bNemotron\b', 'custom classifier', fm)

    if fm != original:
        p.write_text("---\n" + fm + "---\n" + parts[2], encoding="utf-8")
```

## Doğrulama

```python
# Kalan izleri kontrol et
for p in repo.rglob("SKILL.md"):
    content = p.read_text(encoding="utf-8", errors="replace")
    for field in ["phase:", "lesson:", "origin:", "tools:", "nemo"]:
        if re.search(rf'\b{field}\b', content, re.IGNORECASE):
            print(f"KALAN: {p} → {field}")
```

## Bu Oturumda

14 Haziran 2026'da 737 dosyada temizlik yapıldı: 486 phase, 486 lesson, 251 origin, 11 tools, 3 nemo tag.
