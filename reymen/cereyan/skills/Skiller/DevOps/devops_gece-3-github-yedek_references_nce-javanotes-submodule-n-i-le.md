
> **Kategori:** DevOps

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Tüm ajanlar |
| **Ne?** | Devops_Gece 3 Github Yedek_References_Nce Javanotes Submodule N I Le |
| **Nerede?** | DevOps/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

# Önce JavaNotes submodule'ünü işle
if [ -f JavaNotes/.git ]; then
  cd JavaNotes
  git add -A 2>/dev/null
  git commit -m "Auto backup submodule $(date +%Y-%m-%d_%H:%M)" 2>/dev/null
  GIT_TERMINAL_PROMPT=0 git push origin main 2>/dev/null &
  cd ..
fi