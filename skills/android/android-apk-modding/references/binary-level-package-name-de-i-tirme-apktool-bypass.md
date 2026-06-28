---
skill_id: c5cb2c7fd0eb
usage_count: 1
last_used: 2026-06-16
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