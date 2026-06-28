
> **Kategori:** DevOps

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Tüm ajanlar |
| **Ne?** | Devops_Gece 3 Github Yedek_References_Pat Test Nce User Ile Ana Hesap Kontrol |
| **Nerede?** | DevOps/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

# PAT test — önce /user ile ana hesap kontrolü
USER_CHECK=$(curl -s -w "\n%{http_code}" -H "Authorization: token <PAT>" https://api.github.com/user)
USER_HTTP=$(echo "$USER_CHECK" | tail -1)
echo "User endpoint HTTP: $USER_HTTP"  # 200=ok, 401/403=token geçersiz