
> **Kategori:** DevOps

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Tüm ajanlar |
| **Ne?** | Devops_Gece 3 Github Yedek_References_Gh Cli Keyring De Kendi Oauth Token Var |
| **Nerede?** | DevOps/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

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