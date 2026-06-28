
> **Kategori:** DevOps

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Tüm ajanlar |
| **Ne?** | Devops_Gece 3 Github Yedek_References_Ssh Ba Ar S Zsa Https Pat Dene |
| **Nerede?** | DevOps/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

# SSH başarısızsa HTTPS+PAT dene
if [ $? -ne 0 ]; then
  PAT=$(grep "^GITHUB_TOKEN=" /c/Users/marko/AppData/Local/hermes/.env | head -1 | cut -d= -f2)
  if [ -n "$PAT" ] && [ "$PAT" != "***" ]; then
    git remote set-url origin "https://Izleyici-Hermes:$PAT@github.com/Izleyici-Hermes/hermes-skills.git"
    GIT_TERMINAL_PROMPT=0 git push origin master 2>/dev/null || GIT_TERMINAL_PROMPT=0 git push origin main 2>/dev/null
  fi
fi
```

### 2. Obsidian Vault Yedek

```bash
cd "/c/Users/marko/OneDrive/Belgeler/Obsidian Vault"