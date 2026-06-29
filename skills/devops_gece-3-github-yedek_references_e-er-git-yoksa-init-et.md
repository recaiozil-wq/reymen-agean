
> **Kategori:** DevOps

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Tüm ajanlar |
| **Ne?** | Devops_Gece 3 Github Yedek_References_E Er Git Yoksa Init Et |
| **Nerede?** | DevOps/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

# Eğer .git yoksa init et
if [ ! -d .git ]; then
  git init
  git remote add origin git@github.com:Izleyici-Hermes/hermes-skills.git
fi

git add -A
git commit -m "Auto backup $(date +%Y-%m-%d_%H:%M)"