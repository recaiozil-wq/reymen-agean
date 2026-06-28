---
name: software-development_self-improvement-loop_references_once-hafiza-schema
description: OnceHafiza — Schema & Migration Reference
title: "Software Development Self Improvement Loop References Once Hafiza Schema"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | OnceHafiza — Schema & Migration Reference |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# OnceHafiza — Schema & Migration Reference

## CREATE TABLE (yeni DB'ler için)

```sql
CREATE TABLE IF NOT EXISTS ogrenmeler (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    hedef TEXT UNIQUE NOT NULL,
    cozum TEXT NOT NULL,
    kaynak TEXT DEFAULT '',
    basari_sayisi INTEGER DEFAULT 1,
    hata_sayisi INTEGER DEFAULT 0,
    son_basari TEXT,
    son_hata TEXT,
    guven_skoru FLOAT DEFAULT 1.0,
    son_kullanim TEXT,
    kategori TEXT DEFAULT '',
    gecerlilik_tarihi TEXT,
    olusturulma TEXT DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_hedef ON ogrenmeler(hedef);
CREATE INDEX IF NOT EXISTS idx_kategori ON ogrenmeler(kategori);
```

## Migration (eski DB'ler için — ALTER TABLE)

```python
for col_sql in [
    "ALTER TABLE ogrenmeler ADD COLUMN guven_skoru FLOAT DEFAULT 1.0",
    "ALTER TABLE ogrenmeler ADD COLUMN son_kullanim TEXT",
    "ALTER TABLE ogrenmeler ADD COLUMN kategori TEXT DEFAULT ''",
    "ALTER TABLE ogrenmeler ADD COLUMN gecerlilik_tarihi TEXT",
]:
    try:
        con.execute(col_sql)
    except sqlite3.OperationalError:
        pass  # kolon zaten var

# Kolon bazlı index'ler migration SONRASI kurulur
for idx_sql in [
    "CREATE INDEX IF NOT EXISTS idx_kategori ON ogrenmeler(kategori)",
]:
    try:
        con.execute(idx_sql)
    except sqlite3.OperationalError:
        pass
```

## INSERT / UPDATE Pattern

### Kaydet (başarı)
```python
# Guven skoru hesapla
guven = round(basari / (basari + hata), 4) if (basari + hata) > 0 else 1.0

# Geçerlilik tarihi: bugün + 6 ay
from datetime import datetime, timezone, timedelta
gelecek = su_an.replace(
    month=su_an.month + 6 if su_an.month <= 6 else su_an.month - 6,
    year=su_an.year + (1 if su_an.month > 6 else 0)
)

con.execute("""
    INSERT INTO ogrenmeler
    (hedef, cozum, kaynak, basari_sayisi, son_basari, son_kullanim,
     guven_skoru, kategori, gecerlilik_tarihi)
    VALUES (?, ?, ?, 1, ?, ?, ?, ?, ?)
    ON CONFLICT(hedef) DO UPDATE SET
        basari_sayisi = basari_sayisi + 1,
        son_basari = excluded.son_basari,
        son_kullanim = excluded.son_kullanim,
        guven_skoru = ?,
        cozum = excluded.cozum,
        kategori = CASE WHEN excluded.kategori != ''
                       THEN excluded.kategori ELSE kategori END
""", (hedef, cozum, kaynak, bugun, bugun, guven, kategori, gecerlilik, guven))
```

### Hata kaydet
```python
# ogrenmeler'de varsa hata_sayisi++ ve guven_skoru güncelle
mevcut = con.execute(
    "SELECT basari_sayisi, hata_sayisi FROM ogrenmeler WHERE hedef = ?",
    (hedef[:500],),
).fetchone()
if mevcut:
    basari = mevcut[0]
    hata_say = mevcut[1] + 1
    toplam = basari + hata_say
    guven = round(basari / toplam, 4) if toplam > 0 else 0.0
    con.execute(
        "UPDATE ogrenmeler SET hata_sayisi = hata_sayisi + 1, "
        "son_hata = datetime('now'), guven_skoru = ? "
        "WHERE hedef = ?",
        (guven, hedef[:500]),
    )
```

### Okuma (cache hit)
```python
# Geçerlilik kontrolü
gecerlilik_asmis = gecerli and gecerli < su_an if gecerli else False

# Güven skoru güncelle
basari, hata = row[2], row[3]
guven = basari / (basari + hata) if (basari + hata) > 0 else 1.0
con.execute(
    "UPDATE ogrenmeler SET basari_sayisi = basari_sayisi + 1, "
    "son_basari = datetime('now'), "
    "son_kullanim = datetime('now'), "
    "guven_skoru = ? WHERE hedef = ?",
    (round(guven, 4), hedef),
)

# Uyarı ekle
sonuc = {"hedef": ..., "cozum": ..., "kaynak": ...}
if gecerlilik_asmis:
    sonuc["uyari"] = f"⚠️ Bu bilginin geçerlilik tarihi {gecerli} — güncelliğini yitirmiş olabilir!"
```

## Dosya
`reymen/sistem/once_hafiza.py` — 500+ satır, tüm OnceHafiza sınıfı + modül-level wrapper'lar + test
