---
skill_id: c2516f9677d8
usage_count: 1
last_used: 2026-06-16
---
# TÜM dosyalar (alt klasör yoluyla birlikte, .md olmadan)
existing = set()
for root, dirs, files in os.walk(VAULT):
    for f in files:
        if f.endswith('.md'):
            rel = os.path.relpath(os.path.join(root, f), VAULT).replace('\\', '/').replace('.md', '')
            existing.add(rel)
            name = f.replace('.md', '')
            existing.add(name)