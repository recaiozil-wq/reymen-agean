
> **Kategori:** Github

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Tüm ajanlar |
| **Ne?** | Github_Github Repo Management_References_Not Skills Scattered In Subdirectories |
| **Nerede?** | Github/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

# NOT skills scattered in subdirectories
```

**Method B — Clone + Python script (full control):**
```bash
git clone --depth 1 https://github.com/owner/repo.git
cd repo
python3 scripts/install_skills.py "/target/skills/dir" --type all --force --json
```

**Method C — Direct copy (single skill dir):**
```bash
cp -r repo/skill-dir ~/.hermes/skills/skill-name
```

### Post-Install

1. Run `skills_list()` to verify appearance
2. Run `skill_view(name)` to check content loaded correctly
3. Run `sync_skills_to_obsidian.py` to sync to vault
4. Test with a simple use case

### Windows-Specific Pitfalls

- `npx skills add` opens an interactive multi-select prompt that hangs in non-PTY terminals. Prefer `--yes` or clone+script approach.
- Paths with spaces in Windows need quoting in scripts but NOT in npx/git commands.
- After install, always verify with `skills_list()` — some skills may silently collide (same name, different source).

| Action | gh | git + curl |
|--------|-----|-----------|
| Clone | `gh repo clone o/r` | `git clone https://github.com/o/r.git` |
| Create repo | `gh repo create name --public` | `curl POST /user/repos` |
| Fork | `gh repo fork o/r --clone` | `curl POST /repos/o/r/forks` + `git clone` |
| Repo info | `gh repo view o/r` | `curl GET /repos/o/r` |
| Edit settings | `gh repo edit --...` | `curl PATCH /repos/o/r` |
| Create release | `gh release create v1.0` | `curl POST /repos/o/r/releases` |
| List workflows | `gh workflow list` | `curl GET /repos/o/r/actions/workflows` |
| Rerun CI | `gh run rerun ID` | `curl POST /repos/o/r/actions/runs/ID/rerun` |
| Set secret | `gh secret set KEY` | `curl PUT /repos/o/r/actions/secrets/KEY` (+ encryption) |