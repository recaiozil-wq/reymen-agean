---
skill_id: a45fde072db4
usage_count: 1
last_used: 2026-06-16
---
# apktool.yml → renameManifestPackage: com.yeni.paket.adi
```

**3) Smali class referanslarını değiştir (EN ÖNEMLİ)**
Sadece manifest rename YETMEZ — DEX içinde `Lcom/eski/paket/Class;` referansları eski kalır:
```bash