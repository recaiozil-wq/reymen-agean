
> **Kategori:** DevOps

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Tüm ajanlar |
| **Ne?** | Devops_Gece 3 Github Yedek_References_Auth Stratejileri Ncelik S Ras Yla |
| **Nerede?** | DevOps/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

## Auth Stratejileri (öncelik sırasıyla)

### Strateji 1: SSH (tercih edilen)
```bash
git remote set-url origin git@github.com:Izleyici-Hermes/<repo>.git
git push origin <branch>
```
**Gereksinim**: `~/.ssh/id_ed25519` SSH key'i GitHub hesabına eklenmiş olmalı.

### Strateji 2: HTTPS + PAT
```bash
git remote set-url origin https://Izleyici-Hermes:<PAT>@github.com/Izleyici-Hermes/<repo>.git
GIT_TERMINAL_PROMPT=0 git push origin <branch>
```
**Gereksinim**: PAT token'ın `repo` scope'u olmalı. Önce `curl -H "Authorization: token <PAT>" https://api.github.com/user` ile doğrula.

**PAT alternatif kaynağı**: `.env`'de `***` maskesi varsa (Hermes maskelemesi nedeniyle), PAT'ı mevcut git remote URL'sinden de okuyabilirsin:
```bash