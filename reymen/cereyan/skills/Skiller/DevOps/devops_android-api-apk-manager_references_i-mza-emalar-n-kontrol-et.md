
> **Kategori:** DevOps

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Tüm ajanlar |
| **Ne?** | Devops_Android Api Apk Manager_References_I Mza Emalar N Kontrol Et |
| **Nerede?** | DevOps/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

# İmza şemalarını kontrol et
apksigner verify --verbose "orijinal.apk" 2>&1 | grep -E "Verified using|WARNING:"
```

#### 3. Decompile Et
```bash
java -jar apktool.jar d -f orijinal.apk -o decompile_out/