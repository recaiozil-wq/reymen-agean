
> **Kategori:** DevOps

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Tüm ajanlar |
| **Ne?** | Devops_Android Api Apk Manager_References_Tekrar Imzala Birle Tirme Imzay Bozar |
| **Nerede?** | DevOps/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

# Tekrar imzala (birleştirme imzayı bozar)
apksigner sign --ks my.keystore --ks-key-alias myalias monolithic.apk
```

Veya manifest'ten split referanslarını temizle, `apktool b` ile yeniden build et.

#### 8. Doğrula
```bash