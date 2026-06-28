
> **Kategori:** DevOps

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Tüm ajanlar |
| **Ne?** | Devops_Hermes Backup Otomasyonu_References_Backup Repo Yapisi |
| **Nerede?** | DevOps/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

# Backup Repo Yapısı — 2026-06-14

## Sorun
`asdafgf/hermes-skills` reposu GitHub'da bulunamıyor (404). Kullanıcı adı değişmiş/silinmiş.

## Yeni Yapı

Tüm Hermes yedekleri **Watcher-Hermes** organizasyonu altında toplanmıştır:

| Repo | İçerik | Push durumu |
|------|--------|-------------|
| Watcher-Hermes/hermes-mouse | Windows otomasyon skill'leri (10 kategori) | ✓ Push başarılı |
| Watcher-Hermes/hermes-skills | Diğer tüm skill'ler (~1.100 SKILL.md) | ✓ Push başarılı (token'lar temizlendi) |
| Watcher-Hermes/obsidian-vault | Obsidian vault yedek | ✓ Push başarılı |

## Token Sorunu
- `.env`'deki GITHUB_TOKEN (93 karakter, fine-grained PAT): `curl` ile repo oluşturma → 403
- `gh` CLI (keyring OAuth, `repo` scope): repo oluşturma ✓
- Obsidian vault git config'deki PAT (66 karakter, fine-grained): sadece obsidian-vault repo'suna push yetkisi var

## Skill Kategorisine Göre Ayırma Yöntemi
1. `cp -r /c/Users/marko/AppData/Local/hermes/skills/windows-automation /hedef/hermes-mouse/skills/`
2. `cd /hedef && git init && git add -A && git commit -m "..." && git remote add origin ... && git push --force origin master`
3. Kalan skill'ler için aynı işlem
4. Token içeren dosyaları (gece-3-github-yedek/references/*.md) sil veya içindeki token'ları kaldır
