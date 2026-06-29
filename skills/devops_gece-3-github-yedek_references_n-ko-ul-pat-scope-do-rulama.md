
> **Kategori:** DevOps

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Tüm ajanlar |
| **Ne?** | Devops_Gece 3 Github Yedek_References_N Ko Ul Pat Scope Do Rulama |
| **Nerede?** | DevOps/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

## ÖN KOŞUL: PAT Scope Doğrulama

PAT ile repo oluşturma/push yapmadan ÖNCE token scope'larını kontrol et:

```python
import urllib.request, json

req = urllib.request.Request("https://api.github.com/user")
req.add_header("Authorization", f"token {TOKEN}")
resp = urllib.request.urlopen(req)
scopes = resp.headers.get("X-OAuth-Scopes", "?")
print(f"Scopes: {scopes}")