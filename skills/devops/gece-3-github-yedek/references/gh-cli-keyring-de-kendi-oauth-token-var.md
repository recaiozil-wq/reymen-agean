---
skill_id: 1ebb9076ffc9
usage_count: 1
last_used: 2026-06-16
---
# gh CLI (keyring'de kendi OAuth token'ı var)
gh repo create Watcher-Hermes/<repo-adi> --public --description "aciklama"
```
`gh` CLI oturumu açık olduğunda (`gh auth status`) MCP GitHub veya PAT olmadan repo oluşturabilir. `asdafgf` 404 verse bile `gh`, token scope'ları (`repo`) sayesinde org altında repo yaratabilir.

**Ne zaman kullanılır:**
- MCP GitHub "Authentication Failed" hatası veriyorsa
- PAT fine-grained scope'a takılıyorsa (403)
- `gh auth status` → "Logged in" gösteriyorsa

### Strateji 4: MCP GitHub push_files (son çare)
```python