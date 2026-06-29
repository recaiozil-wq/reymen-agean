
> **Kategori:** DevOps

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Tüm ajanlar |
| **Ne?** | Devops_Gece 3 Github Yedek_References_Ba Ar S Zsa Pat Dene |
| **Nerede?** | DevOps/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

# Başarısızsa PAT dene
if [ $? -ne 0 ]; then
  PAT=$(grep "^GITHUB_TOKEN=" /c/Users/marko/AppData/Local/hermes/.env | head -1 | cut -d= -f2)
  if [ -n "$PAT" ] && [ "$PAT" != "***" ]; then
    git remote set-url origin "https://Watcher-Hermes:$PAT@github.com/Watcher-Hermes/obsidian-vault.git"
    GIT_TERMINAL_PROMPT=0 git push origin "$BRANCH"
  fi
fi
```

### 3. Telegram Bildirimi

```python