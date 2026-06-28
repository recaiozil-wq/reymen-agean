---
skill_id: a8f28cc6a1f9
usage_count: 1
last_used: 2026-06-16
---
# TÜM linkler
broken = {}
for root, dirs, files in os.walk(VAULT):
    for f in files:
        if not f.endswith('.md'):
            continue
        path = os.path.join(root, f)
        with open(path, 'r', encoding='utf-8', errors='replace') as fh:
            content = fh.read()
        rel = os.path.relpath(path, VAULT).replace('\\', '/')
        for m in re.finditer(r'\[\[([^\]]+?)\]\]', content):
            target = m.group(1).split('|')[0].strip()
            bare = target.split('#')[0]
            if bare not in existing:
                found = False
                for e in existing:
                    if e.endswith('/' + bare):
                        found = True
                        break
                if not found and not bare.startswith('http'):
                    if rel not in broken:
                        broken[rel] = []
                    broken[rel].append(target)

print(f"Kırık link: {sum(len(v) for v in broken.values())}")
for src, links in sorted(broken.items()):
    for l in links:
        print(f"  {src} -> [[{l}]]")
```

**Hedef:** 0 gerçek kırık link (Rusça/İngilizce dış kaynak notları hariç).

### 1. Vault Durum Tespiti

```python
import re
from pathlib import Path

VAULT = Path(r"C:\Users\marko\OneDrive\Belgeler\Obsidian Vault")