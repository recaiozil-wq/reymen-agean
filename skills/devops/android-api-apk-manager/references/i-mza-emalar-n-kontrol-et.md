---
skill_id: a8da66c42c02
usage_count: 1
last_used: 2026-06-16
---
# İmza şemalarını kontrol et
apksigner verify --verbose "orijinal.apk" 2>&1 | grep -E "Verified using|WARNING:"
```

#### 3. Decompile Et
```bash
java -jar apktool.jar d -f orijinal.apk -o decompile_out/