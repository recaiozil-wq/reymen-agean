---
skill_id: f2768f99961f
usage_count: 1
last_used: 2026-06-16
---
# Çıktı "Verified using v1, v2, v3 scheme" içermeli
```

Sadece v1 görünüyorsa → jarsigner ile imzalamışsındır, başa dön.
"ERROR: JAR signer" hatası → zipalign atlanmış olabilir, adım 4'e dön.

---

### Adım 6 — DOĞRULA (En Değerli Adım)

Çoğu skill bu adımı atlar ve "tamam" der. Sonra uygulama açılışta çöker. **Bu adım atlanamaz.**

**6a — Cihaza kur:**

**Sistem uygulaması tespiti (Google ön yüklü uygulamaları, Samsung apps):**
```bash