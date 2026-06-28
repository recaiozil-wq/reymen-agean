
> **Kategori:** DevOps

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Tüm ajanlar |
| **Ne?** | Devops_Android Api Apk Manager_References_Apk Modding Decompile Modify Rebuild Sign |
| **Nerede?** | DevOps/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

## APK Modding (Decompile → Modify → Rebuild → Sign)

Varolan bir APK'yı tersine mühendislik ile değiştirmek için bu workflow'u izle.

### Gereksinimler
- `apktool.jar` (en son sürüm, indir: `https://github.com/iBotPeaches/Apktool/releases`)
- `uber-apk-signer.jar` (isteğe bağlı, imza için)
- `jarsigner` veya `apksigner` (JDK ile gelir)
- Java JDK 17+
- `aapt2` (Android SDK build-tools içinde)

### Adımlar

#### 1. APK İndir
```bash