---
skill_id: fb24c0ef559a
usage_count: 1
last_used: 2026-06-16
---
# Tüm wikilink'leri tara
for md in sorted(all_md):
    content = md.read_text(encoding="utf-8", errors="replace")
    found = re.findall(r'\[\[([^\]|#]+?)(?:[|#][^\]]*)?\]\]', content)
    for link in found: