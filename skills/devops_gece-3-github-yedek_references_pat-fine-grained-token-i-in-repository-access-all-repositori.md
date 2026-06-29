
> **Kategori:** DevOps

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Tüm ajanlar |
| **Ne?** | Devops_Gece 3 Github Yedek_References_Pat Fine Grained Token I In Repository Access All Repositori |
| **Nerede?** | DevOps/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

# PAT fine-grained token IÇIN: Repository access → All repositories → Read and Write
```

**Önemli**: Token'ı `curl` veya `urllib` ile kullanırken TOKEN değişkenini shell'de set et — `export GH_TOKEN=<token>` ve `curl -H "Authorization: token $GH_TOKEN"`. Hermes `.env`'deki maskeyi kaldırmaz; gerçek token'ı memory'den veya binary `open()` ile oku.

Eğer `repo` scope'u yoksa veya token geçersizse (401/403):
1. Kullanıcıdan GitHub'da yeni PAT oluşturmasını iste (Settings → Developer settings → Tokens)
2. `repo` ve `workflow` scope'larını işaretle
3. Yeni token'ı `.env`'ye yaz (binary `open('...', 'wb')` ile)