---
name: ortak-bilgi-deposu_references_db-schema
description: OnceHafiza DB Şeması
title: "Ortak Bilgi Deposu References Db Schema"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | OnceHafiza DB Şeması |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# OnceHafiza DB Şeması

## Tablo: ogrenmeler

```sql
CREATE TABLE ogrenmeler (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    hedef           TEXT NOT NULL UNIQUE,        -- Görev adı (arama anahtarı)
    kategori        TEXT NOT NULL DEFAULT 'genel', -- "kali/network", "windows/terminal", "dron", "cad"
    icerik          TEXT NOT NULL,               -- Çözüm içeriği
    guven_skoru     REAL NOT NULL DEFAULT 1.0,   -- basari/(basari+hata) — sigmoid
    basari_sayisi   INTEGER NOT NULL DEFAULT 1,  -- Kaç kez başarılı
    hata_sayisi     INTEGER NOT NULL DEFAULT 0,  -- Kaç kez hata
    son_kullanim    TEXT NOT NULL DEFAULT (date('now')),  -- Son okuma
    gecerlilik_tarihi TEXT NOT NULL DEFAULT (date('now', '+180 days')), -- Bugün+6ay
    olusturulma     TEXT NOT NULL DEFAULT (datetime('now')),
    guncelleme      TEXT NOT NULL DEFAULT (datetime('now')),
    web_arama_sebebi TEXT DEFAULT '',            -- Tetikleyici notu
    kaynak_url      TEXT DEFAULT NULL            -- Kaynak link
);

CREATE INDEX idx_ogrenmeler_kategori ON ogrenmeler(kategori);
CREATE INDEX idx_ogrenmeler_hedef   ON ogrenmeler(hedef);
CREATE INDEX idx_ogrenmeler_gecerli ON ogrenmeler(gecerlilik_tarihi);
```

## Örnek Kayıt

```sql
INSERT OR IGNORE INTO ogrenmeler 
    (hedef, kategori, icerik, guven_skoru, basari_sayisi, son_kullanim, gecerlilik_tarihi, kaynak_url)
VALUES 
    ('nmap_port_tarama', 'kali/network/nmap', 'nmap -sV -p- hedef_ip', 
     0.8, 5, '2026-06-21', '2026-12-21', 'hermes_memory');
```

## Kategori Dağılımı

| Ajan | Kategori | Örnek |
|:-----|:---------|:------|
| 🐉 Kali | `kali/network/*`, `kali/web/*`, `kali/network/nmap` | `kali/network/nmap` |
| 🪟 Windows | `windows/terminal/*`, `windows/terminal/network` | `windows/terminal/network` |
| 🏗 CAD | `cad/*`, `dron` | `cad/solidworks` |
| 🤖 Hermes | `kullanici/*`, `sistem/*`, `video/*` | `kullanici/profil` |
| 🎬 Video | `video/learning`, `video/python/nmap` | `video/learning` |
| 🔗 Cross | `cross-platform/*`, `test` | `cross-platform/network` |

## Migration (eski DB)

```python
def _db_kur():
    c.execute("""CREATE TABLE IF NOT EXISTS ogrenmeler (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        hedef TEXT NOT NULL,
        kategori TEXT NOT NULL DEFAULT 'genel',
        icerik TEXT NOT NULL,
        guven_skoru REAL NOT NULL DEFAULT 1.0,
        basari_sayisi INTEGER NOT NULL DEFAULT 1,
        hata_sayisi INTEGER NOT NULL DEFAULT 0,
        son_kullanim TEXT NOT NULL DEFAULT (date('now')),
        gecerlilik_tarihi TEXT NOT NULL DEFAULT (date('now', '+180 days')),
        olusturulma TEXT NOT NULL DEFAULT (datetime('now')),
        guncelleme TEXT NOT NULL DEFAULT (datetime('now'))
    )""")
    # Sütun ekleme (eski DB varsa hata vermez)
    for col in [
        "ALTER TABLE ogrenmeler ADD COLUMN web_arama_sebebi TEXT DEFAULT ''",
        "ALTER TABLE ogrenmeler ADD COLUMN kaynak_url TEXT DEFAULT NULL"
    ]:
        try: c.execute(col)
        except: pass
```
