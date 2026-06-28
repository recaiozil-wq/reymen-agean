
> **Kategori:** android

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Tüm ajanlar |
| **Ne?** | Android_Android Apk Modding_References_Apktool Yml Renamemanifestpackage Com Yeni Paket Adi |
| **Nerede?** | android/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

# apktool.yml → renameManifestPackage: com.yeni.paket.adi
```

**3) Smali class referanslarını değiştir (EN ÖNEMLİ)**
Sadece manifest rename YETMEZ — DEX içinde `Lcom/eski/paket/Class;` referansları eski kalır:
```bash