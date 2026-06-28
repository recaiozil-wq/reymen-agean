---
skill_id: 61cc8abe2b51
usage_count: 1
last_used: 2026-06-16
---
## Merge APK Rebuild — Resource Compilation Hataları

Split APK'yı merge ettikten sonra apktool rebuild'te `invalid value for type 'X'. Expected a reference` hatası alınırsa:

**Sebep:** Merge script'i values-*/ dizinlerindeki XML'lerde boolean değerleri yanlış tip bağlamında bırakır.

**Toplu düzeltme:** Tüm XML'leri tara, `>true</item>` veya `>false</item>` içeren satırları sil. Bu genelde anims.xml, layouts.xml, xmls.xml, animators.xml, drawables.xml, styles.xml, fonts.xml, interpolators.xml, menus.xml dosyalarında olur.

İkinci hata: `public.xml: no definition for declared symbol` — merge'de public.xml güncellenmemiştir. O zaman merge APK'yı bırak, orijinal split + base APK'yı ayrı imzalayıp `adb install-multiple` dene.