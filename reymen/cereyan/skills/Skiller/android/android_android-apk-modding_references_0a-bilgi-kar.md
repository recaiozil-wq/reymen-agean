
> **Kategori:** android

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Tüm ajanlar |
| **Ne?** | Android_Android Apk Modding_References_0A Bilgi Kar |
| **Nerede?** | android/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

# 0a — Bilgi çıkar
$APKTOOL d -f -o _preview/ target.apk
```

**KONTROL 0:** Şu soruları cevapla:

| Soru | Nasıl Bakılır |
|------|-------------|
| **targetSdkVersion kaç?** | `grep targetSdk _preview/apktool.yml` |
| **İmza şeması?** | `apksigner verify target.apk` (varsa) |
| **Native lib var mı?** | `ls _preview/lib/` boş mu dolu mu? |
| **Obfuscation var mı?** | `ls _preview/smali/*/` — harf isimleri (a.smali, b.smali) varsa R8/ProGuard var |
| **Split APK mı?** | `grep isSplitRequired _preview/AndroidManifest.xml` |
| **minSdkVersion?** | `grep minSdk _preview/apktool.yml` |
| **Package name?** | `grep package _preview/AndroidManifest.xml` |

```bash