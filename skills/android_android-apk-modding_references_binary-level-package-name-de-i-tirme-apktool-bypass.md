
> **Kategori:** android

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Tüm ajanlar |
| **Ne?** | Android_Android Apk Modding_References_Binary Level Package Name De I Tirme Apktool Bypass |
| **Nerede?** | android/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

## Binary-level Package Name Değiştirme (apktool bypass)

apktool bazı APK'lerde "Paket geçersiz" hatası üretir. Güvenli alternatif:

Python ile binary AndroidManifest.xml'de UTF-16LE string değiştir:
```python
import zipfile
orig = "com.google.audio.hearing.visualization.accessibility.scribe"
new_pkg = "com.live.transcribe.hermes.twentyfourhours.extended.android"
assert len(orig) == len(new_pkg), "Uzunluklar esit olmali!"
with zipfile.ZipFile("target.apk", "r") as z:
    manifest = z.read("AndroidManifest.xml")
new_manifest = manifest.replace(orig.encode('utf-16-le'), new_pkg.encode('utf-16-le'))