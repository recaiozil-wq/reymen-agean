
> **Kategori:** android

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Tüm ajanlar |
| **Ne?** | Android_Android Apk Modding_References_Merge Apk Rebuild Resource Compilation Hatalar |
| **Nerede?** | android/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

## Merge APK Rebuild — Resource Compilation Hataları

Split APK'yı merge ettikten sonra apktool rebuild'te `invalid value for type 'X'. Expected a reference` hatası alınırsa:

**Sebep:** Merge script'i values-*/ dizinlerindeki XML'lerde boolean değerleri yanlış tip bağlamında bırakır.

**Toplu düzeltme:** Tüm XML'leri tara, `>true</item>` veya `>false</item>` içeren satırları sil. Bu genelde anims.xml, layouts.xml, xmls.xml, animators.xml, drawables.xml, styles.xml, fonts.xml, interpolators.xml, menus.xml dosyalarında olur.

İkinci hata: `public.xml: no definition for declared symbol` — merge'de public.xml güncellenmemiştir. O zaman merge APK'yı bırak, orijinal split + base APK'yı ayrı imzalayıp `adb install-multiple` dene.