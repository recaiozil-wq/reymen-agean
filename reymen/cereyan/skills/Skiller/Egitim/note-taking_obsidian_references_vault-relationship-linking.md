
> **Kategori:** Egitim

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Tüm ajanlar |
| **Ne?** | Note Taking_Obsidian_References_Vault Relationship Linking |
| **Nerede?** | Egitim/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

# Vault Relationship Linking

Strategy for connecting related notes in Obsidian vault via
`[[wikilinks]]` and Map of Content (MOC) notes.

## Scan Phase

1. List all `.md` files in the vault with `search_files(target="files")`.
2. For each file, extract:
   - `tags` (from frontmatter or inline)
   - `related_skills` / `Ilgili Skill'ler` lists
   - Skill/note name keywords
   - Shared technical domain references
3. Build a relationship matrix: which notes share tags, reference each
   other, or belong to overlapping domains.

## Link Architecture

Three-tier approach, applied in order:

### Tier 1: MOC (Map of Content) notes
Create one MOC per broad domain at the vault root (e.g.,
`Hermes/MOC - Yapay Zeka Ekosistemi.md`). Each MOC:
- Lists related category `[[index]]` notes
- Lists category-to-category cross-references
- Lives at the vault root so it catches attention in Graph View

### Tier 2: Category-index cross-links
Each category `_index.md` gets a header line pointing to its parent MOC:
```
**[[_index]]**  |  **[[MOC - Parent MOC|← MOC]]**
```

### Tier 3: Per-note cross-category links
Individual notes that span categories get a `## Cross-category links`
section listing sibling notes in OTHER categories. Use relative
wikilinks: `[[../other-category/note-name|display text]]`.

## Execution Pattern (Iterative Batch Linking)

For applying 50+ links across 15+ notes, use this loop:

### Step 1: Read the target note's last section
```python
from hermes_tools import read_file
f = read_file(path, tail=5)
# Find the last heading: look for "## " or "---" in the tail
# If "## Ilgili Skill'ler" or "## Related skills" already exists,
# append after it. Otherwise find the true last section.
```

### Step 2: Patch with `## Cross-category links`
Anchor the patch on the section heading right before the natural
insertion point. Typical anchors:
- `## Common Pitfalls` (if present) → insert Cross-category links before it
- `## Key Rules` → same
- `## Doğrulama` → same
- Last `##` heading in the file → insert after it

### Step 3: Priority ordering for which notes to link
1. **Category index files** (`_index.md`) → link to parent MOC first
2. **Hub/umbrella notes** (Hibrit AI, hermes-agent) → link to sub-skills
3. **Skill notes that reference other categories** (e.g., vscode-otomasyon → windows-automation)
4. **Cron/Knowledge notes** → link back to active skills

### Step 4: Validation
After all patches are applied, spot-check with:
```python
import re
from pathlib import Path
v = Path(r"C:\Users\marko\OneDrive\Belgeler\Obsidian Vault"
         r"\Hermes")
for md in sorted(v.rglob("*.md")):
    c = md.read_text(encoding="utf-8", errors="replace")
    if "## Cross-category links" in c:
        links = re.findall(r'\(\.\.[^)]+\)', c)
        for l in links:
            target = l.split("|")[0].strip("()")
            # target is relative; resolve if possible
        print(f"{md.stem}: {len(links)} links")
```

### Step 5: Bootstrap (10-15 patched notes is a good stopping point)
Don't try to link all 100+ files in one session. Cover:
- All category index files
- All root/umbrella notes
- 3-5 most cross-category-relevant skill notes per MOC

Then update the MOC notes themselves to include the new links.

## Pitfalls

- Do NOT add circular links (A→B→A in the same section).
- Do NOT link to deleted/missing notes — verify each target exists.
- MOC notes should be idempotent: safe to rewrite entirely on refresh.
- Relative paths work only when both source and target are inside the
  vault; prefer them over full absolute links.
- Use descriptive link titles (`[[target|Kısa Açıklama]]`) so Graph View
  edges are readable.
- **Python 3.14 token interpolation**: When the token value contains `***`
  (triple-asterisk patterns), Python string formatting breaks. Use
  string concatenation (`part1 + part2`) instead of f-strings.
- **patch anchor must be unique**: If `## Common Pitfalls` appears
  identically in two places (e.g., list items start the same way),
  the fuzzy matcher may hit the wrong one. Include a unique snippet of
  the *first list item under that heading* for safe anchoring.
- **Don't patch notes with "Ilgili Skill'ler" that already cover the link**:
  Check first — no point adding a cross-category link if it's already
  listed in the existing related-skills section.
- **Keep session scope manageable**: 15 patched notes + 3 MOC updates
  + 1 validation is a good session. Over 25 patches and you risk
  context window overflow or mismatched anchors.
